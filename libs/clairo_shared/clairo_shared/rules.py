"""Business rules: strict claim validation and status transitions.

Implements BR-1..BR-9 from the U1 functional design business-rules.md.
Functions return result tuples where applicable.
"""

from __future__ import annotations

from decimal import Decimal

from .errors import TransitionError, ValidationError
from .models import CanonicalClaim, ClaimStatus
from .result import Result, err, ok

# Allowed status transitions (BR-7).
_ALLOWED_TRANSITIONS: dict[ClaimStatus, set[ClaimStatus]] = {
    ClaimStatus.RECEIVED: {
        ClaimStatus.INTAKE_COMPLETE,
        ClaimStatus.REJECTED,
        ClaimStatus.FAILED,
    },
    ClaimStatus.INTAKE_COMPLETE: {ClaimStatus.ADJUDICATED, ClaimStatus.FAILED},
    ClaimStatus.ADJUDICATED: {ClaimStatus.COMPLIANCE_CHECKED, ClaimStatus.FAILED},
    ClaimStatus.COMPLIANCE_CHECKED: {
        ClaimStatus.DECIDED,
        ClaimStatus.PENDING_REVIEW,
        ClaimStatus.FAILED,
    },
    ClaimStatus.PENDING_REVIEW: {ClaimStatus.DECIDED, ClaimStatus.FAILED},
    # Terminal states (BR-8): no outgoing transitions.
    ClaimStatus.DECIDED: set(),
    ClaimStatus.REJECTED: set(),
    ClaimStatus.FAILED: set(),
}


def validate_claim(claim: CanonicalClaim) -> Result:
    """Strict validation (BR-1..BR-5). Returns (claim, None) or (None, ValidationError)."""
    if not claim.claimant or not claim.claimant.name.strip():
        return err(ValidationError("Claim must have a claimant name (BR-1)"))

    if not claim.line_items:
        return err(ValidationError("Claim must have at least one line item (BR-2)"))

    for idx, li in enumerate(claim.line_items):
        if not li.procedure_code or not str(li.procedure_code).strip():
            return err(
                ValidationError(f"Line item {idx} missing procedure_code (BR-3)")
            )
        if li.amount is None or li.amount <= Decimal("0"):
            return err(
                ValidationError(f"Line item {idx} must have a positive amount (BR-3)")
            )

    if claim.total_amount is None or claim.total_amount < Decimal("0"):
        return err(ValidationError("total_amount must be present and non-negative (BR-4)"))

    if not claim.currency or len(claim.currency) != 3:
        return err(ValidationError("currency must be a 3-letter ISO 4217 code (BR-5)"))

    return ok(claim)


def can_transition(current: ClaimStatus, target: ClaimStatus) -> bool:
    """True if the status transition is allowed (BR-7..BR-9)."""
    return target in _ALLOWED_TRANSITIONS.get(current, set())


def check_transition(current: ClaimStatus, target: ClaimStatus) -> Result:
    """Validate a transition. Returns (target, None) or (None, TransitionError)."""
    if can_transition(current, target):
        return ok(target)
    return err(
        TransitionError(
            f"Invalid status transition: {current.value} -> {target.value} (BR-9)"
        )
    )


def total_matches_line_items(claim: CanonicalClaim) -> bool:
    """BR-4 soft check: does total_amount equal the sum of line-item amounts?"""
    line_sum = sum((li.amount for li in claim.line_items), Decimal("0"))
    return line_sum == claim.total_amount
