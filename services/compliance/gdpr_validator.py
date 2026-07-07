"""GDPR Validator: pure-LLM evaluation of a claim + decision against the
externalized GDPR policy text (CR-1, CR-2).

The GDPR policy doc is loaded from S3 at the location referenced by the SSM
`gdpr_rules_ref` parameter. Bedrock client is injectable.
"""

from __future__ import annotations

import json
import os

import boto3

from clairo_shared.models import ComplianceFindings

_SYSTEM_PROMPT = (
    "You are a GDPR compliance reviewer for health insurance claim decisions. "
    "Given the GDPR policy text, a claim summary, and a preliminary decision, "
    "assess compliance and return ONLY JSON: "
    '{"compliant": true|false, "anomalies": [string], '
    '"gdpr_flags": [string], "rationale": string}. '
    "Do not change the decision; only assess compliance."
)


class GdprValidator:
    def __init__(self, bedrock_client=None, model_id: str = None):
        self._bedrock = bedrock_client or boto3.client(
            "bedrock-runtime", region_name=os.environ.get("AWS_REGION", "us-east-1")
        )
        self._model_id = model_id or os.environ.get(
            "BEDROCK_MODEL_ID", "anthropic.claude-3-5-sonnet-20240620-v1:0"
        )

    def validate(self, rules_text: str, claim_summary: str, decision_summary: str) -> ComplianceFindings:
        """Evaluate compliance. Returns ComplianceFindings (never raises)."""
        user_text = (
            f"GDPR POLICY:\n{rules_text}\n\n"
            f"CLAIM:\n{claim_summary}\n\n"
            f"DECISION:\n{decision_summary}"
        )
        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 1500,
            "system": _SYSTEM_PROMPT,
            "messages": [{"role": "user", "content": [{"type": "text", "text": user_text}]}],
        }
        try:
            response = self._bedrock.invoke_model(
                modelId=self._model_id, body=json.dumps(body)
            )
            payload = json.loads(response["body"].read())
            parsed = self._parse_json(payload["content"][0]["text"])
        except Exception as exc:
            # Conservative fallback (CR-11): flag as non-compliant anomaly, do not block.
            return ComplianceFindings(
                compliant=False,
                anomalies=[f"compliance evaluation error: {exc}"],
                gdpr_flags=[],
            )

        if parsed is None:
            return ComplianceFindings(
                compliant=False,
                anomalies=["compliance output could not be parsed"],
                gdpr_flags=[],
            )

        return ComplianceFindings(
            compliant=bool(parsed.get("compliant", False)),
            anomalies=[str(a) for a in parsed.get("anomalies", []) or []],
            gdpr_flags=[str(f) for f in parsed.get("gdpr_flags", []) or []],
        )

    @staticmethod
    def _parse_json(text: str):
        text = (text or "").strip()
        if text.startswith("```"):
            text = text.strip("`")
            if text.lower().startswith("json"):
                text = text[4:]
        start = text.find("{")
        end = text.rfind("}")
        if start == -1 or end == -1 or end < start:
            return None
        try:
            return json.loads(text[start : end + 1])
        except json.JSONDecodeError:
            return None
