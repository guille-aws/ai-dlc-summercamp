"""LLM Extractor: single structured-output prompt to Bedrock Claude Sonnet
(IR-5, Q2:A). Returns a parsed canonical-claim dict.

boto3 bedrock-runtime client is injectable for offline verification.
"""

from __future__ import annotations

import json
import os

import boto3

from clairo_shared.errors import ValidationError
from clairo_shared.result import Result, err, ok

_SYSTEM_PROMPT = (
    "You are a health insurance claim data extractor. Given raw text extracted "
    "from claim documents, return ONLY a JSON object matching this schema: "
    '{"claimant": {"name": str, "claimant_id": str|null}, '
    '"provider": str|null, "policy_ref": str|null, '
    '"line_items": [{"procedure_code": str, "diagnosis_code": str|null, '
    '"amount": number, "service_date": "YYYY-MM-DD"|null}], '
    '"total_amount": number, "currency": str}. '
    "Do not include any prose, only the JSON object."
)


class LlmExtractor:
    def __init__(self, bedrock_client=None, model_id: str = None):
        self._bedrock = bedrock_client or boto3.client(
            "bedrock-runtime",
            region_name=os.environ.get("AWS_REGION", "us-east-1"),
        )
        self._model_id = model_id or os.environ.get(
            "BEDROCK_MODEL_ID", "anthropic.claude-3-5-sonnet-20240620-v1:0"
        )

    def extract(self, raw_text: str) -> Result:
        """Return (claim_dict, None) or (None, ValidationError)."""
        if not raw_text or not raw_text.strip():
            return err(ValidationError("No text available for extraction"))

        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 2000,
            "system": _SYSTEM_PROMPT,
            "messages": [
                {"role": "user", "content": [{"type": "text", "text": raw_text}]}
            ],
        }
        try:
            response = self._bedrock.invoke_model(
                modelId=self._model_id, body=json.dumps(body)
            )
            payload = json.loads(response["body"].read())
            text_out = payload["content"][0]["text"]
        except Exception as exc:
            return err(ValidationError(f"LLM extraction failed: {exc}"))

        claim_dict = self._parse_json(text_out)
        if claim_dict is None:
            return err(ValidationError("LLM did not return valid JSON"))
        return ok(claim_dict)

    @staticmethod
    def _parse_json(text: str):
        """Defensively parse JSON, tolerating code fences or surrounding text."""
        text = text.strip()
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
