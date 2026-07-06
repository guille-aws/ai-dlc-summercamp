"""Reasoner: builds the RAG prompt, parses the generated structured output into a
PreliminaryDecision, clamps confidence, and applies weak-basis handling.
"""

from __future__ import annotations

import json

from clairo_shared.models import (
    CanonicalClaim,
    DecisionOutcome,
    PolicyCitation,
    PreliminaryDecision,
)

from .types import RetrievalResult

PROMPT_INSTRUCTIONS = (
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


def to_decision(retrieval: RetrievalResult) -> PreliminaryDecision:
    """Map the RAG generated text into a PreliminaryDecision (AR-5..AR-9, AR-11)."""
    parsed = _parse_json(retrieval.generated_text)

    if parsed is None:
        # Unusable output -> low-confidence needs_more_info (AR-11), routes to human.
        return PreliminaryDecision(
            outcome=DecisionOutcome.NEEDS_MORE_INFO,
            confidence=0.0,
            reasoning_chain=["Adjudicator output could not be parsed; routing to human review."],
            citations=[PolicyCitation.from_dict(
                {"source_id": p.source_id, "excerpt": p.excerpt, "score": p.score}
            ) for p in retrieval.passages],
        )

    try:
        outcome = DecisionOutcome(parsed.get("outcome", "needs_more_info"))
    except ValueError:
        outcome = DecisionOutcome.NEEDS_MORE_INFO

    confidence = _clamp(parsed.get("confidence", 0.0))

    # Weak retrieval basis -> cap confidence low so it routes to human (AR-9).
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
