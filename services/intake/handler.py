"""Intake Lambda handler.

Entry point for the U2 Intake agent. Invoked by the orchestrator (API path) or
via S3-upload event (US-02). Routes documents by content type, merges extracted
text, runs LLM extraction + normalization, persists the claim, and audits.

Status outcomes: IntakeComplete (success), Rejected (unreadable/invalid, IR-8),
Failed (unrecoverable, IR-10).
"""

from __future__ import annotations

import os

from clairo_shared.audit import AuditLogger
from clairo_shared.models import ActorType, ClaimStatus, DocumentRef
from clairo_shared.repositories.claim_repository import ClaimRepository
from clairo_shared.repositories.document_store import DocumentStore
from clairo_shared.util import get_logger, log_event, new_claim_id

from .extraction import IntakeInput, IntakeResult, is_ocr_type, is_text_type
from .llm_extractor import LlmExtractor
from .normalizer import Normalizer
from .ocr_adapter import OcrAdapter
from .text_parser import TextParser

_logger = get_logger("clairo.intake")


class IntakeService:
    """Composable intake service with injectable dependencies (offline testable)."""

    def __init__(
        self,
        claim_repo: ClaimRepository = None,
        document_store: DocumentStore = None,
        audit: AuditLogger = None,
        ocr_adapter: OcrAdapter = None,
        text_parser: TextParser = None,
        llm_extractor: LlmExtractor = None,
        normalizer: Normalizer = None,
    ):
        self.claim_repo = claim_repo or ClaimRepository()
        self.document_store = document_store or DocumentStore()
        self.audit = audit or AuditLogger()
        self.ocr = ocr_adapter or OcrAdapter()
        self.text_parser = text_parser or text_parser_default(self.document_store)
        self.llm = llm_extractor or LlmExtractor()
        self.normalizer = normalizer or Normalizer()

    def process(self, intake_input: IntakeInput) -> IntakeResult:
        claim_id = intake_input.claim_id or new_claim_id()

        # 1. Extract from each document, routing by content type.
        merged_blocks = []
        evidence = []
        for ref in intake_input.documents:
            extracted, error = self._extract_one(ref)
            if error:
                return self._reject(claim_id, f"extraction failed: {error}")
            merged_blocks.extend(extracted.blocks)
            for block in extracted.blocks:
                evidence.append((ref, block.page, block.bbox))

        raw_text = "\n".join(b.text for b in merged_blocks)
        if not raw_text.strip():
            return self._reject(claim_id, "no usable text extracted")

        # 2. LLM extraction -> canonical dict.
        claim_dict, error = self.llm.extract(raw_text)
        if error:
            return self._reject(claim_id, f"llm extraction: {error}")

        # 3. Normalize + strict validate.
        claim, error = self.normalizer.normalize(claim_id, claim_dict, evidence)
        if error:
            return self._reject(claim_id, f"validation: {error}")

        # 4. Persist claim, advance status, audit.
        claim.status = ClaimStatus.INTAKE_COMPLETE
        _, perr = self.claim_repo.create_claim(claim)
        if perr:
            return self._fail(claim_id, f"persist failed: {perr}")

        self.audit.append(
            claim_id=claim_id,
            actor="intake-agent",
            actor_type=ActorType.AGENT,
            step="intake",
            detail={"documents": len(intake_input.documents), "status": "IntakeComplete"},
        )
        log_event(_logger, "intake_complete", claim_id=claim_id)
        return IntakeResult(claim=claim, evidence_blocks=evidence)

    def _extract_one(self, ref: DocumentRef):
        if is_ocr_type(ref.content_type):
            return self.ocr.extract(ref)
        if is_text_type(ref.content_type):
            return self.text_parser.parse(ref)
        # IR-3: unsupported type
        from clairo_shared.errors import ValidationError
        from clairo_shared.result import err

        return err(ValidationError(f"unsupported document type: {ref.content_type}"))

    def _reject(self, claim_id: str, reason: str) -> IntakeResult:
        self.audit.append(
            claim_id=claim_id,
            actor="intake-agent",
            actor_type=ActorType.AGENT,
            step="intake",
            detail={"status": "Rejected", "reason": reason},
        )
        log_event(_logger, "intake_rejected", claim_id=claim_id, reason=reason)
        return IntakeResult(claim=None, rejected_reason=reason)

    def _fail(self, claim_id: str, reason: str) -> IntakeResult:
        self.audit.append(
            claim_id=claim_id,
            actor="intake-agent",
            actor_type=ActorType.AGENT,
            step="intake",
            detail={"status": "Failed", "reason": reason},
        )
        log_event(_logger, "intake_failed", claim_id=claim_id, reason=reason)
        return IntakeResult(claim=None, rejected_reason=reason)


def text_parser_default(document_store) -> TextParser:
    return TextParser(document_store)


def _parse_event(event: dict) -> IntakeInput:
    """Build IntakeInput from an orchestrator invoke or S3/EventBridge event."""
    # Orchestrator invoke: {"claim_id":..., "documents":[{bucket,key,content_type}], "submitted_by":...}
    if "documents" in event:
        docs = [DocumentRef.from_dict(d) for d in event["documents"]]
        return IntakeInput(
            documents=docs,
            claim_id=event.get("claim_id"),
            submitted_by=event.get("submitted_by"),
        )

    # S3 via EventBridge: detail.bucket.name + detail.object.key
    detail = event.get("detail", {})
    bucket = detail.get("bucket", {}).get("name")
    key = detail.get("object", {}).get("key")
    content_type = _guess_content_type(key or "")
    docs = [DocumentRef(bucket=bucket, key=key, content_type=content_type)] if bucket and key else []
    return IntakeInput(documents=docs)


def _guess_content_type(key: str) -> str:
    lower = key.lower()
    if lower.endswith(".pdf"):
        return "application/pdf"
    if lower.endswith((".png", ".jpg", ".jpeg", ".tiff")):
        return "image/" + lower.rsplit(".", 1)[-1]
    if lower.endswith(".eml"):
        return "message/rfc822"
    return "text/plain"


def handler(event, context=None):
    """AWS Lambda entry point."""
    service = IntakeService()
    intake_input = _parse_event(event)
    result = service.process(intake_input)
    if result.claim is not None:
        return {
            "statusCode": 200,
            "claim_id": result.claim.claim_id,
            "status": result.claim.status.value,
        }
    return {
        "statusCode": 422,
        "claim_id": intake_input.claim_id,
        "status": ClaimStatus.REJECTED.value,
        "reason": result.rejected_reason,
    }
