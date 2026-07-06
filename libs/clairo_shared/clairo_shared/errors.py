"""Error types used across CLAIRO shared components.

These are returned (not raised) inside result tuples: ``(value, error)``.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ClairoError:
    """Base error carried in a result tuple."""

    message: str
    code: str = "ERROR"

    def __str__(self) -> str:  # pragma: no cover - trivial
        return f"[{self.code}] {self.message}"


@dataclass(frozen=True)
class ValidationError(ClairoError):
    code: str = "VALIDATION_ERROR"


@dataclass(frozen=True)
class NotFoundError(ClairoError):
    code: str = "NOT_FOUND"


@dataclass(frozen=True)
class AuthorizationError(ClairoError):
    code: str = "AUTHORIZATION_ERROR"


@dataclass(frozen=True)
class TransitionError(ClairoError):
    code: str = "TRANSITION_ERROR"


@dataclass(frozen=True)
class StorageError(ClairoError):
    code: str = "STORAGE_ERROR"
