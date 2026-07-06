"""Utility helpers for CLAIRO shared components."""

from __future__ import annotations

import json
import logging
import secrets
import uuid
from datetime import datetime, timezone


def new_claim_id() -> str:
    """Generate a unique claim identifier."""
    return str(uuid.uuid4())


def now_iso() -> str:
    """Current UTC time as an ISO-8601 string with microseconds."""
    return datetime.now(timezone.utc).isoformat()


def new_audit_seq() -> str:
    """Timestamp-based, lexically-sortable audit sequence value.

    Format: ``<ISO-8601 UTC timestamp>-<4 hex chars>``. Microsecond precision
    plus a random suffix makes same-claim collisions negligible for MVP volumes
    (NFR design Q2:A).
    """
    return f"{now_iso()}-{secrets.token_hex(2)}"


def get_logger(name: str = "clairo") -> logging.Logger:
    """Return a logger configured for structured (JSON-ish) CloudWatch output."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("%(message)s"))
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger


def log_event(logger: logging.Logger, event: str, **fields) -> None:
    """Emit a structured log line."""
    payload = {"event": event, "ts": now_iso(), **fields}
    logger.info(json.dumps(payload, default=str))
