"""Intake-internal working types for extraction (see U2 domain-entities.md)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from clairo_shared.models import DocumentRef


@dataclass
class ExtractedBlock:
    text: str
    page: int = 1
    bbox: Optional[list] = None  # [x, y, w, h]


@dataclass
class ExtractedText:
    blocks: list  # list[ExtractedBlock]
    source_ref: DocumentRef

    def full_text(self) -> str:
        return "\n".join(b.text for b in self.blocks)


@dataclass
class IntakeInput:
    documents: list  # list[DocumentRef]
    claim_id: Optional[str] = None
    submitted_by: Optional[str] = None


@dataclass
class IntakeResult:
    claim: object  # CanonicalClaim
    rejected_reason: Optional[str] = None
    evidence_blocks: list = field(default_factory=list)


def is_ocr_type(content_type: str) -> bool:
    """IR-1: PDF and image content types go to Textract."""
    ct = (content_type or "").lower()
    return ct == "application/pdf" or ct.startswith("image/")


def is_text_type(content_type: str) -> bool:
    """IR-2: text and email content types go to the parser."""
    ct = (content_type or "").lower()
    return ct.startswith("text/") or ct == "message/rfc822"
