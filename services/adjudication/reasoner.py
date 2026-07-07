"""Reasoner: builds the RAG prompt from retrieved passages, invokes the Bedrock
model, parses the structured output into a PreliminaryDecision, clamps
confidence, and applies weak-basis handling.
"""

from __future__ import annotations

import json
import os

import boto3

from clairo_shared.models import (
    CanonicalClaim,
    DecisionOutcome,
    PolicyCitation,
    PreliminaryDecision,
)

from types_ import RetrievalResult

_SYSTEM_PROMPT = (
    "You are a health insurance claims adjudicator. Using ONLY the retrieved "
    "policy context, decide the claim and return ONLY a JSON object: "
    '{"outcome": "approve|deny|partial|needs_more_info", '
    '"confidence": number between 0 and 1, '
    '"reasoning_chain": [string, ...], '
    '"citations": [{"source_id": string, "excerpt": string}]}. '
    "If the policy basis is weak or missing, return low confidence."
)


def build_query(claim: CanonicalClaim) -> str:
    lines = [
        f"Claimant: {claim.claimant.name}",
        f"Provider: {claim.provider or 'N/A'}",
        f"Policy: {claim.policy_ref or 'N/A'}",
        f"Total: {claim.total_amount} {claim.currency}",
        "Line items:",
    ]
    for li in claim.line_items:
        lines.append(
            f"  - procedure={li.procedure_code} diagnosis={li.diagnosis_code} "
            f"amount={li.amount} date={li.service_date}"
        )
    return "\n".join(lines)


class Reasoner:
    def __init__(self, bedrock_client=None, model_id: str = None):
        self._bedrock = bedrock_client or boto3.client(
            "bedrock-runtime", region_name=os.environ.get("AWS_REGION", "us-east-1")
        )
        self._model_id = model_id or os.environ.get(
            "BEDROCK_MODEL_ID", "us.anthropic.claude-sonnet-4-5-20250929-v1:0"
        )

    def decide(self, claim: CanonicalClaim, retrieval: RetrievalResult) -> PreliminaryDecision:
        """Invoke the model over claim + retrieved passages -> PreliminaryDecision."""
        context = "\n\n".join(
            f"[{p.source_id}] {p.excerpt}" for p in retrieval.passages
        ) or "(no policy context retrieved)"
        user_text = f"POLICY CONTEXT:\n{context}\n\nCLAIM:\n{build_query(claim)}"

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
            text_out = payload["content"][0]["text"]
        except Exception:
            text_out = ""

        return to_decision(text_out, retrieval)


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


def _clamp(value) -> float:
    try:
        v = float(value)
    except (TypeError, ValueError):
        return 0.0
    return max(0.0, min(1.0, v))


def to_decision(generated_text: str, retrieval: RetrievalResult) -> PreliminaryDecision:
    """Map model output into a PreliminaryDecision (AR-5..AR-9, AR-11)."""
    parsed = _parse_json(generated_text)

    if parsed is None:
        return PreliminaryDecision(
            outcome=DecisionOutcome.NEEDS_MORE_INFO,
            confidence=0.0,
            reasoning_chain=["Adjudicator output could not be parsed; routing to human review."],
            citations=[
                PolicyCitation(source_id=p.source_id, excerpt=p.excerpt, score=p.score)
                for p in retrieval.passages
            ],
        )

    try:
        outcome = DecisionOutcome(parsed.get("outcome", "needs_more_info"))
    except ValueError:
        outcome = DecisionOutcome.NEEDS_MORE_INFO

    confidence = _clamp(parsed.get("confidence", 0.0))
    if retrieval.weak:
        confidence = min(confidence, 0.3)

    reasoning = parsed.get("reasoning_chain") or []
    if retrieval.weak:
        reasoning = list(reasoning) + ["Policy basis was weak or missing (low-confidence)."]

    citations = []
    for c in parsed.get("citations", []) or []:
        citations.append(
            PolicyCitation(
                source_id=str(c.get("source_id", "")),
                excerpt=str(c.get("excerpt", "")),
                score=float(c.get("score", 0.0) or 0.0),
            )
        )
    if not citations:
        citations = [
            PolicyCitation(source_id=p.source_id, excerpt=p.excerpt, score=p.score)
            for p in retrieval.passages
        ]

    return PreliminaryDecision(
        outcome=outcome,
        confidence=confidence,
        reasoning_chain=[str(r) for r in reasoning],
        citations=citations,
    )
