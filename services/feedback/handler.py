"""Feedback Lambda handler (U6).

Triggered by an EventBridge ClaimOverridden event. Builds a corrective example
and writes it to the knowledge base source bucket, then triggers a KB ingestion
job so future adjudications can retrieve it (US-08, FR-5.x).
"""

from __future__ import annotations

import os

import boto3

from clairo_shared.audit import AuditLogger
from clairo_shared.models import ActorType, ReviewerDecision
from clairo_shared.repositories.claim_repository import ClaimRepository
from clairo_shared.util import get_logger, log_event

_logger = get_logger("clairo.feedback")


def build_corrective_example(claim, decision: ReviewerDecision) -> str:
    """Claim summary + final overridden decision + reviewer rationale (Q1:A)."""
    claimant = claim.claimant.name if claim and claim.claimant else "Unknown"
    total = f"{claim.total_amount} {claim.currency}" if claim else "N/A"
    lines = [
        f"# Corrective Example - Claim {decision_claim_id(claim)}",
        "",
        "## Claim Summary",
        f"- Claimant: {claimant}",
        f"- Total: {total}",
        "",
        "## Final Decision (Human Override)",
        f"- Outcome: {decision.outcome.value}",
        f"- Rationale: {decision.rationale}",
        f"- Reviewer: {decision.reviewer_id}",
    ]
    return "\n".join(lines)


def decision_claim_id(claim) -> str:
    return claim.claim_id if claim else "unknown"


class FeedbackService:
    def __init__(
        self,
        claim_repo: ClaimRepository = None,
        audit: AuditLogger = None,
        s3_client=None,
        bedrock_agent_client=None,
        kb_source_bucket: str = None,
        kb_id: str = None,
        kb_data_source_id: str = None,
    ):
        self.claim_repo = claim_repo or ClaimRepository()
        self.audit = audit or AuditLogger()
        self._s3 = s3_client or boto3.client(
            "s3", region_name=os.environ.get("AWS_REGION", "us-east-1")
        )
        self._bedrock_agent = bedrock_agent_client or boto3.client(
            "bedrock-agent", region_name=os.environ.get("AWS_REGION", "us-east-1")
        )
        self._bucket = kb_source_bucket or os.environ.get("KB_SOURCE_BUCKET", "clairo-dev-kb-source")
        self._kb_id = kb_id or os.environ.get("KB_ID", "")
        self._data_source_id = kb_data_source_id or os.environ.get("KB_DATA_SOURCE_ID", "")

    def process(self, claim_id: str, decision: ReviewerDecision) -> None:
        claim, _ = self.claim_repo.get_claim(claim_id)
        content = build_corrective_example(claim, decision)
        key = f"corrective/{claim_id}.md"  # deterministic (Q4:A)

        # Write corrective example to kb-source (best-effort).
        try:
            self._s3.put_object(
                Bucket=self._bucket, Key=key,
                Body=content.encode("utf-8"), ContentType="text/markdown",
            )
        except Exception as exc:
            log_event(_logger, "feedback_s3_failed", claim_id=claim_id, error=str(exc))
            self._audit(claim_id, {"status": "failed", "stage": "s3_put", "error": str(exc)})
            return

        # Trigger KB ingestion (best-effort).
        ingestion_status = "skipped"
        if self._kb_id and self._data_source_id:
            try:
                self._bedrock_agent.start_ingestion_job(
                    knowledgeBaseId=self._kb_id, dataSourceId=self._data_source_id
                )
                ingestion_status = "started"
            except Exception as exc:
                log_event(_logger, "feedback_ingestion_failed", claim_id=claim_id, error=str(exc))
                ingestion_status = f"error: {exc}"

        self._audit(claim_id, {"s3_key": key, "ingestion": ingestion_status})
        log_event(_logger, "feedback_complete", claim_id=claim_id, ingestion=ingestion_status)

    def _audit(self, claim_id: str, detail: dict) -> None:
        self.audit.append(
            claim_id=claim_id, actor="feedback-agent",
            actor_type=ActorType.AGENT, step="feedback", detail=detail,
        )


def _parse_events(event: dict):
    """Yield (claim_id, ReviewerDecision) from EventBridge ClaimOverridden event(s)."""
    # EventBridge single event: {"detail-type": "ClaimOverridden", "detail": {...}}
    records = event.get("Records") or [event]
    for rec in records:
        detail = rec.get("detail", rec)
        claim_id = detail.get("claim_id")
        decision_dict = detail.get("decision", {})
        if not claim_id:
            continue
        try:
            decision = ReviewerDecision.from_dict(decision_dict)
        except Exception:
            continue
        yield claim_id, decision


def handler(event, context=None):
    """AWS Lambda entry point (EventBridge)."""
    service = FeedbackService()
    count = 0
    for claim_id, decision in _parse_events(event):
        service.process(claim_id, decision)
        count += 1
    return {"statusCode": 200, "processed": count}
