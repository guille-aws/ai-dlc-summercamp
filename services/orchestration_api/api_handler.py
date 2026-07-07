"""Claim API handler (API Gateway proxy integration).

Role-scoped endpoints (US-01/06/07/09/10/11), Cognito principal + per-endpoint
role checks (Q6:A / OR-15..OR-17). Heavy work happens async via the pipeline.
"""

from __future__ import annotations

import json

from clairo_shared.audit import AuditLogger
from clairo_shared.auth import (
    ROLE_REVIEWER,
    ROLE_SUPERVISOR,
    principal_from_event,
    require_any_role,
    require_role,
)
from clairo_shared.config import ConfigProvider
from clairo_shared.models import (
    ActorType,
    CanonicalClaim,
    Claimant,
    ClaimStatus,
    DecisionOutcome,
    LineItem,
    ReviewerDecision,
)
from clairo_shared.repositories.claim_repository import ClaimRepository
from clairo_shared.util import get_logger, new_claim_id, now_iso
from decimal import Decimal

from review import ReviewTaskManager

_logger = get_logger("clairo.api")


def _response(status: int, body: dict) -> dict:
    return {"statusCode": status, "headers": {"Content-Type": "application/json"},
            "body": json.dumps(body, default=str)}


class ApiHandler:
    def __init__(
        self,
        claim_repo: ClaimRepository = None,
        audit: AuditLogger = None,
        config: ConfigProvider = None,
        reviews: ReviewTaskManager = None,
    ):
        self.claim_repo = claim_repo or ClaimRepository()
        self.audit = audit or AuditLogger()
        self.config = config or ConfigProvider()
        self.reviews = reviews or ReviewTaskManager()

    def handle(self, event: dict) -> dict:
        principal, aerr = principal_from_event(event)
        if aerr:
            return _response(401, {"error": str(aerr)})

        method = event.get("httpMethod", "")
        resource = event.get("resource", "")  # API GW resource template
        path_params = event.get("pathParameters") or {}
        body = self._parse_body(event)

        # Route dispatch.
        if resource == "/claims" and method == "POST":
            return self._create_claim(principal, body)
        if resource == "/claims/{id}" and method == "GET":
            return self._get_claim(principal, path_params.get("id"))
        if resource == "/claims/{id}/audit" and method == "GET":
            return self._get_audit(principal, path_params.get("id"))
        if resource == "/reviews" and method == "GET":
            return self._list_reviews(principal)
        if resource == "/reviews/{taskId}" and method == "POST":
            return self._submit_review(principal, path_params.get("taskId"), body)
        if resource == "/config/threshold" and method == "PUT":
            return self._set_threshold(principal, body)
        return _response(404, {"error": "not found"})

    # --- Endpoints ---

    def _create_claim(self, principal, body) -> dict:
        # US-01: any authenticated submitter can create.
        claim_id = new_claim_id()
        try:
            claimant = Claimant(name=(body.get("claimant") or {}).get("name", "Unknown"))
            line_items = [
                LineItem(
                    procedure_code=li.get("procedure_code", ""),
                    amount=Decimal(str(li.get("amount", "0"))),
                    diagnosis_code=li.get("diagnosis_code"),
                    service_date=li.get("service_date"),
                )
                for li in body.get("line_items", [])
            ]
            total = Decimal(str(body.get("total_amount", "0")))
            claim = CanonicalClaim(
                claim_id=claim_id, claimant=claimant, line_items=line_items,
                total_amount=total, currency=body.get("currency", "EUR"),
                provider=body.get("provider"), policy_ref=body.get("policy_ref"),
                status=ClaimStatus.RECEIVED, created_at=now_iso(),
            )
        except Exception as exc:
            return _response(400, {"error": f"invalid claim payload: {exc}"})

        _, error = self.claim_repo.create_claim(claim)
        if error:
            return _response(500, {"error": str(error)})
        self.audit.append(claim_id=claim_id, actor=principal.user_id,
                          actor_type=ActorType.USER, step="submit",
                          detail={"status": "Received"})
        return _response(201, {"claim_id": claim_id, "status": ClaimStatus.RECEIVED.value})

    def _get_claim(self, principal, claim_id) -> dict:
        claim, error = self.claim_repo.get_claim(claim_id)
        if error:
            return _response(404, {"error": str(error)})
        return _response(200, claim.to_dict())

    def _get_audit(self, principal, claim_id) -> dict:
        # US-11: Supervisor only.
        _, rerr = require_role(principal, ROLE_SUPERVISOR)
        if rerr:
            return _response(403, {"error": str(rerr)})
        trail, error = self.audit.get_trail(claim_id)
        if error:
            return _response(500, {"error": str(error)})
        return _response(200, {"claim_id": claim_id, "audit": [e.to_dict() for e in trail]})

    def _list_reviews(self, principal) -> dict:
        # US-06: Reviewer or Supervisor.
        _, rerr = require_any_role(principal, [ROLE_REVIEWER, ROLE_SUPERVISOR])
        if rerr:
            return _response(403, {"error": str(rerr)})
        claims, error = self.reviews.list_tasks()
        if error:
            return _response(500, {"error": str(error)})
        return _response(200, {"tasks": [c.claim_id for c in claims]})

    def _submit_review(self, principal, claim_id, body) -> dict:
        # US-07: Reviewer or Supervisor.
        _, rerr = require_any_role(principal, [ROLE_REVIEWER, ROLE_SUPERVISOR])
        if rerr:
            return _response(403, {"error": str(rerr)})
        try:
            outcome = DecisionOutcome(body.get("outcome"))
        except (ValueError, TypeError):
            return _response(400, {"error": "invalid outcome"})
        decision = ReviewerDecision(
            outcome=outcome, reviewer_id=principal.user_id,
            is_override=bool(body.get("is_override", False)),
            rationale=body.get("rationale", ""), timestamp=now_iso(),
        )
        result, error = self.reviews.submit_review(claim_id, decision)
        if error:
            return _response(400, {"error": str(error)})
        return _response(200, result)

    def _set_threshold(self, principal, body) -> dict:
        # US-10: Supervisor only.
        _, rerr = require_role(principal, ROLE_SUPERVISOR)
        if rerr:
            return _response(403, {"error": str(rerr)})
        try:
            value = float(body.get("threshold"))
        except (ValueError, TypeError):
            return _response(400, {"error": "invalid threshold"})
        _, error = self.config.set_threshold(value)
        if error:
            return _response(400, {"error": str(error)})
        return _response(200, {"threshold": value})

    @staticmethod
    def _parse_body(event: dict) -> dict:
        raw = event.get("body")
        if not raw:
            return {}
        try:
            return json.loads(raw)
        except (json.JSONDecodeError, TypeError):
            return {}


def handler(event, context=None):
    """AWS Lambda entry point (API Gateway proxy)."""
    return ApiHandler().handle(event)
