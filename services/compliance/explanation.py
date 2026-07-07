"""Explanation Generator: builds audit-ready JSON + Markdown explanation
documents (CR-7, CR-8) from claim + decision + compliance findings.
"""

from __future__ import annotations

import json

from clairo_shared.models import CanonicalClaim, ComplianceFindings, PreliminaryDecision


def build_json(
    claim: CanonicalClaim, decision: PreliminaryDecision, findings: ComplianceFindings
) -> str:
    payload = {
        "claim_id": claim.claim_id,
        "claimant": claim.claimant.name,
        "total_amount": str(claim.total_amount),
        "currency": claim.currency,
        "decision": {
            "outcome": decision.outcome.value,
            "confidence": decision.confidence,
            "reasoning_chain": decision.reasoning_chain,
            "citations": [c.to_dict() for c in decision.citations],
        },
        "compliance": {
            "compliant": findings.compliant,
            "anomalies": findings.anomalies,
            "gdpr_flags": findings.gdpr_flags,
        },
    }
    return json.dumps(payload, indent=2, default=str)


def build_markdown(
    claim: CanonicalClaim, decision: PreliminaryDecision, findings: ComplianceFindings
) -> str:
    lines = [
        f"# Claim Explanation - {claim.claim_id}",
        "",
        "## Claim Summary",
        f"- Claimant: {claim.claimant.name}",
        f"- Total: {claim.total_amount} {claim.currency}",
        f"- Line items: {len(claim.line_items)}",
        "",
        "## Decision",
        f"- Outcome: **{decision.outcome.value}**",
        f"- Confidence: {decision.confidence}",
        "",
        "### Reasoning",
    ]
    for step in decision.reasoning_chain:
        lines.append(f"- {step}")
    lines += ["", "### Policy Citations"]
    for c in decision.citations:
        lines.append(f"- {c.source_id}: {c.excerpt}")
    lines += [
        "",
        "## Compliance (GDPR)",
        f"- Compliant: {findings.compliant}",
    ]
    if findings.gdpr_flags:
        lines.append("- GDPR flags:")
        lines += [f"  - {f}" for f in findings.gdpr_flags]
    if findings.anomalies:
        lines.append("- Anomalies:")
        lines += [f"  - {a}" for a in findings.anomalies]
    return "\n".join(lines)
