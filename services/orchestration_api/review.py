"""Review Task Manager + Evidence Highlighter (US-06, US-07).

Review tasks are claims with status=PendingReview (status GSI, Q3:A). Overrides
emit an EventBridge ClaimOverridden event (Q5:A).
"""

from __future__ import annotations

import json
import os

import boto3

from clairo_shared import rules
from clairo_shared.audit import AuditLogger
from clairo_shared.models import ActorType, ClaimStatus, ReviewerDecision
from clairo_shared.repositories.claim_repository import ClaimRepository
from clairo_shared.result import Result, err, ok
from clairo_shared.errors import TransitionError, ValidationError
from clairo_shared.util import now_iso


def highlight_evidence(claim) -> list:
    """Build highlighted evidence (page + bbox) from the claim's evidence_refs."""
    highlights = []
    for ev in claim.evidence_refs:
        highlights.append(
            {
                "document": ev.document_ref.key if ev.document_ref else None,
                "page": ev.page,
                "bbox": ev.bbox,
            }
        )
    return highlights


class ReviewTaskManager:
    def __init__(
        self,
        claim_repo: ClaimRepository = None,
        audit: AuditLogger = None,
        events_client=None,
        event_bus: str = None,
    ):
        self.claim_repo = claim_repo or ClaimRepository()
        self.audit = audit or AuditLogger()
        self._events = events_client or boto3.client(
            "events", region_name=os.environ.get("AWS_REGION", "us-east-1")
        )
        self._event_bus = event_bus or os.environ.get("EVENT_BUS", "default")

    def list_tasks(self) -> Result:
        """List pending-review claims (US-06)."""
        return self.claim_repo.list_by_status(ClaimStatus.PENDING_REVIEW)

    def get_task(self, claim_id: str) -> Result:
        """Assemble a review task view for a claim."""
        claim, error = self.claim_repo.get_claim(claim_id)
        if error:
            return err(error)
        task = {
            "claim_id": claim.claim_id,
            "status": claim.status.value,
            "highlighted_evidence": highlight_evidence(claim),
        }
        return ok(task)

    def submit_review(self, claim_id: str, decision: ReviewerDecision) -> Result:
        """Record a reviewer decision, finalize, and emit override event if needed."""
        claim, error = self.claim_repo.get_claim(claim_id)
        if error:
            return err(error)
        if claim.status != ClaimStatus.PENDING_REVIEW:
            return err(ValidationError("Claim is not pending review (OR-14)"))

        decision.timestamp = decision.timestamp or now_iso()

        # Record the human decision (audit, FR-4.4 / OR-12).
        self.audit.append(
            claim_id=claim_id,
            actor=decision.reviewer_id,
            actor_type=ActorType.USER,
            step="human_review",
            detail={
                "outcome": decision.outcome.value,
                "is_override": decision.is_override,
                "rationale": decision.rationale,
            },
        )

        # Persist decision + finalize (OR-10).
        self.claim_repo.update_result(claim_id, "review", decision.to_dict())
        _, terr = rules.check_transition(claim.status, ClaimStatus.DECIDED)
        if terr:
            return err(terr)
        self.claim_repo.update_status(claim_id, ClaimStatus.DECIDED)

        # Emit override event (Q5:A / OR-13).
        if decision.is_override:
            self._emit_override(claim_id, decision)

        return ok({"claim_id": claim_id, "status": ClaimStatus.DECIDED.value})

    def _emit_override(self, claim_id: str, decision: ReviewerDecision) -> None:
        try:
            self._events.put_events(
                Entries=[
                    {
                        "Source": f"{_APP}.review",
                        "DetailType": "ClaimOverridden",
                        "Detail": json.dumps(
                            {"claim_id": claim_id, "decision": decision.to_dict()}
                        ),
                        "EventBusName": self._event_bus,
                    }
                ]
            )
        except Exception:
            # Non-fatal for the review action; feedback loop is best-effort.
            pass


_APP = "clairo"
