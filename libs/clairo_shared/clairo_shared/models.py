"""CLAIRO domain models.

Implemented as dataclasses with manual (de)serialization helpers (FD Q6:B).
Decimals and datetimes are represented as strings for DynamoDB-safe storage.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum
from typing import Any, Optional


class ClaimStatus(str, Enum):
    RECEIVED = "Received"
    INTAKE_COMPLETE = "IntakeComplete"
    ADJUDICATED = "Adjudicated"
    COMPLIANCE_CHECKED = "ComplianceChecked"
    PENDING_REVIEW = "PendingReview"
    DECIDED = "Decided"
    REJECTED = "Rejected"
    FAILED = "Failed"


class DecisionOutcome(str, Enum):
    APPROVE = "approve"
    DENY = "deny"
    PARTIAL = "partial"
    NEEDS_MORE_INFO = "needs_more_info"


class ActorType(str, Enum):
    SYSTEM = "system"
    AGENT = "agent"
    USER = "user"


@dataclass
class DocumentRef:
    bucket: str
    key: str
    content_type: str = "application/octet-stream"

    def to_dict(self) -> dict:
        return {"bucket": self.bucket, "key": self.key, "content_type": self.content_type}

    @staticmethod
    def from_dict(d: dict) -> "DocumentRef":
        return DocumentRef(
            bucket=d["bucket"],
            key=d["key"],
            content_type=d.get("content_type", "application/octet-stream"),
        )


@dataclass
class EvidenceRef:
    document_ref: DocumentRef
    page: Optional[int] = None
    bbox: Optional[list] = None

    def to_dict(self) -> dict:
        return {
            "document_ref": self.document_ref.to_dict(),
            "page": self.page,
            "bbox": self.bbox,
        }

    @staticmethod
    def from_dict(d: dict) -> "EvidenceRef":
        return EvidenceRef(
            document_ref=DocumentRef.from_dict(d["document_ref"]),
            page=d.get("page"),
            bbox=d.get("bbox"),
        )


@dataclass
class Claimant:
    name: str
    claimant_id: Optional[str] = None

    def to_dict(self) -> dict:
        return {"name": self.name, "claimant_id": self.claimant_id}

    @staticmethod
    def from_dict(d: dict) -> "Claimant":
        return Claimant(name=d.get("name", ""), claimant_id=d.get("claimant_id"))


@dataclass
class LineItem:
    procedure_code: str
    amount: Decimal
    diagnosis_code: Optional[str] = None
    service_date: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "procedure_code": self.procedure_code,
            "amount": str(self.amount),
            "diagnosis_code": self.diagnosis_code,
            "service_date": self.service_date,
        }

    @staticmethod
    def from_dict(d: dict) -> "LineItem":
        return LineItem(
            procedure_code=d["procedure_code"],
            amount=Decimal(str(d.get("amount", "0"))),
            diagnosis_code=d.get("diagnosis_code"),
            service_date=d.get("service_date"),
        )


@dataclass
class CanonicalClaim:
    claim_id: str
    claimant: Claimant
    line_items: list  # list[LineItem]
    total_amount: Decimal
    status: ClaimStatus = ClaimStatus.RECEIVED
    currency: str = "EUR"
    provider: Optional[str] = None
    policy_ref: Optional[str] = None
    evidence_refs: list = field(default_factory=list)  # list[EvidenceRef]
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    schema_version: str = "1.0"

    def to_dict(self) -> dict:
        return {
            "claim_id": self.claim_id,
            "claimant": self.claimant.to_dict(),
            "line_items": [li.to_dict() for li in self.line_items],
            "total_amount": str(self.total_amount),
            "status": self.status.value,
            "currency": self.currency,
            "provider": self.provider,
            "policy_ref": self.policy_ref,
            "evidence_refs": [e.to_dict() for e in self.evidence_refs],
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "schema_version": self.schema_version,
        }

    @staticmethod
    def from_dict(d: dict) -> "CanonicalClaim":
        return CanonicalClaim(
            claim_id=d["claim_id"],
            claimant=Claimant.from_dict(d.get("claimant", {})),
            line_items=[LineItem.from_dict(li) for li in d.get("line_items", [])],
            total_amount=Decimal(str(d.get("total_amount", "0"))),
            status=ClaimStatus(d.get("status", ClaimStatus.RECEIVED.value)),
            currency=d.get("currency", "EUR"),
            provider=d.get("provider"),
            policy_ref=d.get("policy_ref"),
            evidence_refs=[EvidenceRef.from_dict(e) for e in d.get("evidence_refs", [])],
            created_at=d.get("created_at"),
            updated_at=d.get("updated_at"),
            schema_version=d.get("schema_version", "1.0"),
        )


@dataclass
class PolicyCitation:
    source_id: str
    excerpt: str
    score: float = 0.0

    def to_dict(self) -> dict:
        return {"source_id": self.source_id, "excerpt": self.excerpt, "score": self.score}

    @staticmethod
    def from_dict(d: dict) -> "PolicyCitation":
        return PolicyCitation(
            source_id=d.get("source_id", ""),
            excerpt=d.get("excerpt", ""),
            score=float(d.get("score", 0.0)),
        )


@dataclass
class PreliminaryDecision:
    outcome: DecisionOutcome
    confidence: float
    reasoning_chain: list = field(default_factory=list)  # list[str]
    citations: list = field(default_factory=list)  # list[PolicyCitation]

    def to_dict(self) -> dict:
        return {
            "outcome": self.outcome.value,
            "confidence": self.confidence,
            "reasoning_chain": list(self.reasoning_chain),
            "citations": [c.to_dict() for c in self.citations],
        }

    @staticmethod
    def from_dict(d: dict) -> "PreliminaryDecision":
        return PreliminaryDecision(
            outcome=DecisionOutcome(d["outcome"]),
            confidence=float(d.get("confidence", 0.0)),
            reasoning_chain=list(d.get("reasoning_chain", [])),
            citations=[PolicyCitation.from_dict(c) for c in d.get("citations", [])],
        )


@dataclass
class ComplianceFindings:
    compliant: bool
    anomalies: list = field(default_factory=list)
    gdpr_flags: list = field(default_factory=list)
    explanation_ref: Optional[DocumentRef] = None

    def to_dict(self) -> dict:
        return {
            "compliant": self.compliant,
            "anomalies": list(self.anomalies),
            "gdpr_flags": list(self.gdpr_flags),
            "explanation_ref": self.explanation_ref.to_dict() if self.explanation_ref else None,
        }

    @staticmethod
    def from_dict(d: dict) -> "ComplianceFindings":
        ref = d.get("explanation_ref")
        return ComplianceFindings(
            compliant=bool(d.get("compliant", False)),
            anomalies=list(d.get("anomalies", [])),
            gdpr_flags=list(d.get("gdpr_flags", [])),
            explanation_ref=DocumentRef.from_dict(ref) if ref else None,
        )


@dataclass
class ReviewerDecision:
    outcome: DecisionOutcome
    reviewer_id: str
    is_override: bool = False
    rationale: str = ""
    timestamp: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "outcome": self.outcome.value,
            "reviewer_id": self.reviewer_id,
            "is_override": self.is_override,
            "rationale": self.rationale,
            "timestamp": self.timestamp,
        }

    @staticmethod
    def from_dict(d: dict) -> "ReviewerDecision":
        return ReviewerDecision(
            outcome=DecisionOutcome(d["outcome"]),
            reviewer_id=d.get("reviewer_id", ""),
            is_override=bool(d.get("is_override", False)),
            rationale=d.get("rationale", ""),
            timestamp=d.get("timestamp"),
        )


@dataclass
class AuditEntry:
    claim_id: str
    seq: str
    timestamp: str
    actor: str
    actor_type: ActorType
    step: str
    detail: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "claim_id": self.claim_id,
            "seq": self.seq,
            "timestamp": self.timestamp,
            "actor": self.actor,
            "actor_type": self.actor_type.value,
            "step": self.step,
            "detail": self.detail,
        }

    @staticmethod
    def from_dict(d: dict) -> "AuditEntry":
        return AuditEntry(
            claim_id=d["claim_id"],
            seq=d["seq"],
            timestamp=d.get("timestamp", ""),
            actor=d.get("actor", ""),
            actor_type=ActorType(d.get("actor_type", ActorType.SYSTEM.value)),
            step=d.get("step", ""),
            detail=d.get("detail", {}),
        )


@dataclass
class Principal:
    user_id: str
    email: str = ""
    roles: list = field(default_factory=list)  # list[str]
