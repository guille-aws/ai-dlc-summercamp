"""Adjudication-internal working types (see U3 domain-entities.md)."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class RetrievedPassage:
    source_id: str
    excerpt: str
    score: float = 0.0


@dataclass
class RetrievalResult:
    generated_text: str
    passages: list = field(default_factory=list)  # list[RetrievedPassage]
    weak: bool = False


# Hardcoded weak-match threshold for the MVP (NFR-U3 Q3:B).
WEAK_MATCH_THRESHOLD = 0.4
