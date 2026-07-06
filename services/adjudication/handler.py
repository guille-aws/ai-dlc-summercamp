"""Adjudication Lambda handler.

Loads a claim (status IntakeComplete), performs managed RAG adjudication, persists
the PreliminaryDecision and advances status to Adjudicated, and audits (US-04).
"""

from __future__ import annotations

from clairo_shared import rules
from clairo_shared.audit import AuditLogger
from clairo_shared.models import ActorType, ClaimStatus
from clairo_shared.repositories.claim_repository import ClaimRepository
from clairo_shared.util import get_logger, log_event

from .kb_client import KbClient
from .reasoner import PROMPT_INSTRUCTIONS, build_query, to_decision

_logger = get_logger("clairo.adjudication")


class AdjudicationService:
    def __init__(
        self,
        claim_repo: ClaimRepository = None,
        audit: AuditLogger = None,
        kb_client: KbClient = None,
    ):
        self.claim_repo = claim_repo or ClaimRepository()
        self.audit = audit or AuditLogger()
        self.kb = kb_client or KbClient()

    def process(self, claim_id: str):
        """Adjudicate a claim. Returns (PreliminaryDecision, None) or (None, error)."""
        claim, error = self.claim_repo.get_claim(claim_id)
        if error:
            return None, error

        # Managed RAG.
        retrieval, rerr = self.kb.retrieve_and_generate(
            build_query(claim), PROMPT_INSTRUCTIONS
        )
        if rerr:
            # Unrecoverable retrieval error -> Failed.
            self.claim_repo.update_status(claim_id, ClaimStatus.FAILED)
            self.audit.append(
                claim_id=claim_id,
                actor="adjudication-agent",
                actor_type=ActorType.AGENT,
                step="adjudication",
                detail={"status": "Failed", "reason": str(rerr)},
            )
            return None, rerr

        decision = to_decision(retrieval)

        # Persist decision + advance status (AR-10).
        self.claim_repo.update_result(
            claim_id, "adjudication", decision.to_dict()
        )
        _, terr = rules.check_transition(claim.status, ClaimStatus.ADJUDICATED)
        if terr is None:
            self.claim_repo.update_status(claim_id, ClaimStatus.ADJUDICATED)

        self.audit.append(
            claim_id=claim_id,
            actor="adjudication-agent",
            actor_type=ActorType.AGENT,
            step="adjudication",
            detail={
                "outcome": decision.outcome.value,
                "confidence": decision.confidence,
                "weak_retrieval": retrieval.weak,
            },
        )
        log_event(
            _logger,
            "adjudication_complete",
            claim_id=claim_id,
            outcome=decision.outcome.value,
            confidence=decision.confidence,
        )
        return decision, None


def handler(event, context=None):
    """AWS Lambda entry point. Expects {"claim_id": ...}."""
    claim_id = event.get("claim_id")
    if not claim_id:
        return {"statusCode": 400, "error": "claim_id required"}

    service = AdjudicationService()
    decision, error = service.process(claim_id)
    if error:
        return {"statusCode": 500, "claim_id": claim_id, "error": str(error)}
    return {
        "statusCode": 200,
        "claim_id": claim_id,
        "outcome": decision.outcome.value,
        "confidence": decision.confidence,
        "status": ClaimStatus.ADJUDICATED.value,
    }
