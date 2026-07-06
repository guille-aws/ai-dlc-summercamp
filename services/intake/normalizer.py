"""Claim Normalizer: maps LLM-extracted dict + evidence into a CanonicalClaim
and runs strict validation (IR-7). Attaches evidence refs (Q5:A).
"""

from __future__ import annotations

from decimal import Decimal, InvalidOperation

from clairo_shared import rules
from clairo_shared.models import (
    CanonicalClaim,
    Claimant,
    ClaimStatus,
    DocumentRef,
    EvidenceRef,
    LineItem,
)
from clairo_shared.result import Result, err, ok
from clairo_shared.errors import ValidationError


def _to_decimal(value) -> Decimal:
    try:
        return Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return Decimal("0")


class Normalizer:
    def normalize(self, claim_id: str, claim_dict: dict, evidence) -> Result:
        """Build and validate a CanonicalClaim.

        Returns (CanonicalClaim, None) or (None, ValidationError).
        evidence: list of (DocumentRef, page, bbox) tuples.
        """
        try:
            claimant_data = claim_dict.get("claimant", {}) or {}
            claimant = Claimant(
                name=claimant_data.get("name", "") or "",
                claimant_id=claimant_data.get("claimant_id"),
            )

            line_items = []
            for li in claim_dict.get("line_items", []) or []:
                line_items.append(
                    LineItem(
                        procedure_code=str(li.get("procedure_code", "") or ""),
                        amount=_to_decimal(li.get("amount", 0)),
                        diagnosis_code=li.get("diagnosis_code"),
                        service_date=li.get("service_date"),
                    )
                )

            total = claim_dict.get("total_amount")
            total_amount = (
                _to_decimal(total)
                if total is not None
                else sum((li.amount for li in line_items), Decimal("0"))
            )

            evidence_refs = [
                EvidenceRef(document_ref=ref, page=page, bbox=bbox)
                for (ref, page, bbox) in (evidence or [])
            ]

            claim = CanonicalClaim(
                claim_id=claim_id,
                claimant=claimant,
                line_items=line_items,
                total_amount=total_amount,
                currency=(claim_dict.get("currency") or "EUR"),
                provider=claim_dict.get("provider"),
                policy_ref=claim_dict.get("policy_ref"),
                evidence_refs=evidence_refs,
                status=ClaimStatus.RECEIVED,
            )
        except Exception as exc:  # defensive: malformed LLM structure
            return err(ValidationError(f"Failed to normalize claim: {exc}"))

        # Strict validation (IR-7 / BR-1..BR-5).
        _, verr = rules.validate_claim(claim)
        if verr:
            return err(verr)
        return ok(claim)
