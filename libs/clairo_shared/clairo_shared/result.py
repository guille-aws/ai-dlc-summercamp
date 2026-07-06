"""Result-tuple helpers for CLAIRO's error-handling convention.

Fallible functions return ``(value, error)``:
- On success: ``(value, None)``
- On failure: ``(None, error)`` where error is a ``ClairoError``.
"""

from __future__ import annotations

from typing import Optional, Tuple, TypeVar

from .errors import ClairoError

T = TypeVar("T")

Result = Tuple[Optional[T], Optional[ClairoError]]


def ok(value: T) -> Result:
    """Return a successful result."""
    return value, None


def err(error: ClairoError) -> Result:
    """Return a failed result."""
    return None, error


def is_ok(result: Result) -> bool:
    """True if the result has no error."""
    return result[1] is None
