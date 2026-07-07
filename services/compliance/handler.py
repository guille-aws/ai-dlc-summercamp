"""Compliance Lambda handler.

Loads an Adjudicated claim + its decision, evaluates GDPR compliance (LLM),
generates JSON + Markdown explanations to S3, persists findings, advances status
to ComplianceChecked, and audits (US-05). Annotate-only (CR-4/CR-5).
"""

from __future__ import annotations

from clairo_shared import rules
from clairo_shared.audit import AuditLogger
from clairo_shared.config import ConfigProvider
from clairo_shared.models import (
    ActorType,
    ClaimStatus,
    ComplianceFindings,
    DocumentRef,
    PreliminaryDecision,
)
from clairo_shared.repositories.claim_repository import ClaimRepository
from clairo_shared.repositories.document_store import DocumentStore
from clairo_shared.util import get_logger, log_event

from explanation import build_json, build_markdown
from gdpr_validator import GdprValidator

_logger = get_logger("clairo.compliance")


def _parse_s3_uri(uri: str):
    """s3://bucket/key -> (bucket, key)."""
    if not uri or not uri.startswith("s3://"):
        return None, None
    rest = uri[len("s3://"):]
    parts = rest.split("/", 1)
    if len(parts) != 2:
        return None, None
    return parts[0], parts[1]


class ComplianceService:
    def __init__(
        self,
        claim_repo: ClaimRepository = None,
        document_store: DocumentStore = None,
        audit: AuditLogger = None,
        config: ConfigProvider = None,
        validator: GdprValidator = None,
    ):
        self.claim_repo = claim_repo or ClaimRepository()
        self.document_store = document_store or DocumentStore()
        self.audit = audit or AuditLogger()
        self.config = config or ConfigProvider()
        self.validator = validator or GdprValidator()

    def process(self, claim_id: str, decision_dict: dict = None):
        """Run compliance for a claim. Returns (ComplianceFindings, None) or (None, error).

        decision_dict: the adjudication PreliminaryDecision (passed by the
        orchestrator). Falls back to a minimal decision if absent.
        """
        claim, error = self.claim_repo.get_claim(claim_id)
        if error:
            return None, error

        decision = self._load_decision(decision_dict)

        # Load GDPR rules text (SSM ref -> S3), CR-1 / NFR-U4-3.
        rules_text, rerr = self._load_rules()
        if rerr:
            self.claim_repo.update_status(claim_id, ClaimStatus.FAILED)
            self.audit.append(
                claim_id=claim_id, actor="compliance-agent",
                actor_type=ActorType.AGENT, step="compliance",
                detail={"status": "Failed", "reason": str(rerr)},
            )
            return None, rerr

        # LLM evaluation (never raises).
        findings = self.validator.validate(
            rules_text=rules_text,
            claim_summary=f"{claim.claimant.name}, total {claim.total_amount} {claim.currency}",
            decision_summary=f"{decision.outcome.value} (confidence {decision.confidence})",
        )

        # Generate + store explanations (JSON + Markdown), CR-7.
        json_doc = build_json(claim, decision, findings)
        md_doc = build_markdown(claim, decision, findings)
        self.document_store.put_document(
            json_doc.encode("utf-8"), f"explanations/{claim_id}.json", "application/json"
        )
        md_ref, _ = self.document_store.put_explanation(claim_id, md_doc)
        if isinstance(md_ref, DocumentRef):
            findings.explanation_ref = md_ref

        # Persist findings + advance status (CR-10). Annotate-only: outcome unchanged.
        self.claim_repo.update_result(claim_id, "compliance", findings.to_dict())
        _, terr = rules.check_transition(claim.status, ClaimStatus.COMPLIANCE_CHECKED)
        if terr is None:
            self.claim_repo.update_status(claim_id, ClaimStatus.COMPLIANCE_CHECKED)

        self.audit.append(
            claim_id=claim_id, actor="compliance-agent",
            actor_type=ActorType.AGENT, step="compliance",
            detail={"compliant": findings.compliant, "gdpr_flags": len(findings.gdpr_flags)},
        )
        log_event(
            _logger, "compliance_complete", claim_id=claim_id,
            compliant=findings.compliant, flags=len(findings.gdpr_flags),
        )
        return findings, None

    def _load_decision(self, decision_dict: dict) -> PreliminaryDecision:
        """Reconstruct the adjudication decision passed by the orchestrator."""
        if isinstance(decision_dict, dict):
            try:
                return PreliminaryDecision.from_dict(decision_dict)
            except Exception:
                pass
        # Minimal fallback if the decision was not supplied.
        from clairo_shared.models import DecisionOutcome
        return PreliminaryDecision(
            outcome=DecisionOutcome.NEEDS_MORE_INFO, confidence=0.0,
            reasoning_chain=["adjudication result unavailable"], citations=[],
        )

    def _load_rules(self):
        ref, error = self.config.get_gdpr_rules_ref()
        if error:
            return None, error
        bucket, key = _parse_s3_uri(ref)
        if not bucket:
            return None, error or _ref_error(ref)
        data, derr = self.document_store.get_document(DocumentRef(bucket=bucket, key=key))
        if derr:
            return None, derr
        return data.decode("utf-8", errors="replace"), None


def _ref_error(ref):
    from clairo_shared.errors import ValidationError
    return ValidationError(f"invalid gdpr_rules_ref: {ref}")


def handler(event, context=None):
    """AWS Lambda entry point. Expects {"claim_id": ...}."""
    claim_id = event.get("claim_id")
    if not claim_id:
        return {"statusCode": 400, "error": "claim_id required"}

    service = ComplianceService()
    findings, error = service.process(claim_id, event.get("decision"))
    if error:
        return {"statusCode": 500, "claim_id": claim_id, "error": str(error)}
    return {
        "statusCode": 200,
        "claim_id": claim_id,
        "compliant": findings.compliant,
        "gdpr_flags": findings.gdpr_flags,
        "status": ClaimStatus.COMPLIANCE_CHECKED.value,
    }
