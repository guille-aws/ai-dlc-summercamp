"""Orchestrator: DynamoDB Streams consumer that chains the agent pipeline
(OR-1..OR-4). On each Claims status change, async-invokes the next agent; on
ComplianceChecked, runs routing to finalize or route to human.
"""

from __future__ import annotations

import json
import os

import boto3

from clairo_shared.audit import AuditLogger
from clairo_shared.models import ActorType, ClaimStatus, PreliminaryDecision
from clairo_shared.repositories.claim_repository import ClaimRepository
from clairo_shared.util import get_logger, log_event

from routing import RoutingEvaluator

_logger = get_logger("clairo.orchestrator")

# status (new image) -> next agent function env var
_NEXT_FUNCTION = {
    ClaimStatus.RECEIVED.value: "INTAKE_FN",
    ClaimStatus.INTAKE_COMPLETE.value: "ADJUDICATION_FN",
    ClaimStatus.ADJUDICATED.value: "COMPLIANCE_FN",
}


class Orchestrator:
    def __init__(
        self,
        lambda_client=None,
        claim_repo: ClaimRepository = None,
        audit: AuditLogger = None,
        routing: RoutingEvaluator = None,
    ):
        self._lambda = lambda_client or boto3.client(
            "lambda", region_name=os.environ.get("AWS_REGION", "us-east-1")
        )
        self.claim_repo = claim_repo or ClaimRepository()
        self.audit = audit or AuditLogger()
        self.routing = routing or RoutingEvaluator()

    def handle_status(self, claim_id: str, new_status: str) -> None:
        """Advance the pipeline based on a claim's new status."""
        # Chain to the next agent for early stages.
        fn_env = _NEXT_FUNCTION.get(new_status)
        if fn_env:
            fn_name = os.environ.get(fn_env)
            if fn_name:
                self._async_invoke(fn_name, {"claim_id": claim_id})
                log_event(_logger, "orchestrator_advance", claim_id=claim_id, next=fn_env)
            return

        # Final routing after compliance.
        if new_status == ClaimStatus.COMPLIANCE_CHECKED.value:
            self._route(claim_id)

    def _route(self, claim_id: str) -> None:
        claim, error = self.claim_repo.get_claim(claim_id)
        if error:
            return
        decision = self._load_decision(claim_id)
        routing = self.routing.evaluate(decision)

        if routing.route == "auto":
            self.claim_repo.update_status(claim_id, ClaimStatus.DECIDED)
            self.audit.append(
                claim_id=claim_id, actor="orchestrator", actor_type=ActorType.SYSTEM,
                step="routing", detail={"route": "auto", "status": "Decided",
                                        "threshold": routing.threshold_used},
            )
            log_event(_logger, "auto_decided", claim_id=claim_id)
        else:
            self.claim_repo.update_status(claim_id, ClaimStatus.PENDING_REVIEW)
            self.audit.append(
                claim_id=claim_id, actor="orchestrator", actor_type=ActorType.SYSTEM,
                step="routing", detail={"route": "human", "status": "PendingReview",
                                        "threshold": routing.threshold_used},
            )
            log_event(_logger, "routed_to_human", claim_id=claim_id)

    def _load_decision(self, claim_id: str) -> PreliminaryDecision:
        """Load the persisted adjudication decision for routing."""
        result, error = self.claim_repo.get_result(claim_id, "adjudication")
        if not error and isinstance(result, dict):
            try:
                return PreliminaryDecision.from_dict(result)
            except Exception:
                pass
        # Fallback: no decision available -> route to human.
        from clairo_shared.models import DecisionOutcome
        return PreliminaryDecision(
            outcome=DecisionOutcome.NEEDS_MORE_INFO, confidence=0.0,
            reasoning_chain=[], citations=[],
        )

    def _async_invoke(self, function_name: str, payload: dict) -> None:
        try:
            self._lambda.invoke(
                FunctionName=function_name,
                InvocationType="Event",
                Payload=json.dumps(payload).encode("utf-8"),
            )
        except Exception as exc:
            log_event(_logger, "invoke_failed", function=function_name, error=str(exc))


def _extract_status_changes(event: dict):
    """Yield (claim_id, new_status) for MODIFY/INSERT stream records where status changed."""
    for record in event.get("Records", []):
        if record.get("eventName") not in ("INSERT", "MODIFY"):
            continue
        ddb = record.get("dynamodb", {})
        new_img = ddb.get("NewImage", {})
        old_img = ddb.get("OldImage", {})
        claim_id = _s(new_img.get("claim_id"))
        new_status = _s(new_img.get("status"))
        old_status = _s(old_img.get("status"))
        if claim_id and new_status and new_status != old_status:
            yield claim_id, new_status


def _s(attr):
    """Extract a string from a DynamoDB stream attribute value."""
    if not attr:
        return None
    return attr.get("S")


def handler(event, context=None):
    """AWS Lambda entry point for DynamoDB Streams."""
    orchestrator = Orchestrator()
    for claim_id, new_status in _extract_status_changes(event):
        orchestrator.handle_status(claim_id, new_status)
    return {"statusCode": 200}
