"""Audit Logger: append-only audit trail in DynamoDB.

Append uses a timestamp-based seq (NFR design Q2:A) — no read-before-write.
Only append (PutItem) and read (Query) are exposed; append-only immutability is
also enforced at the IAM level (PutItem-only roles).
"""

from __future__ import annotations

import os
from typing import Optional

import boto3
from boto3.dynamodb.conditions import Key

from .errors import StorageError
from .models import ActorType, AuditEntry
from .result import Result, err, ok
from .util import new_audit_seq, now_iso


class AuditLogger:
    def __init__(self, table_name: Optional[str] = None, dynamodb_resource=None):
        self._table_name = table_name or os.environ.get("AUDIT_TABLE", "clairo-dev-audit")
        self._dynamodb = dynamodb_resource or boto3.resource("dynamodb")
        self._table = self._dynamodb.Table(self._table_name)

    def append(
        self,
        claim_id: str,
        actor: str,
        actor_type: ActorType,
        step: str,
        detail: Optional[dict] = None,
    ) -> Result:
        """Append an immutable audit entry. Returns (AuditEntry, None) or (None, StorageError)."""
        entry = AuditEntry(
            claim_id=claim_id,
            seq=new_audit_seq(),
            timestamp=now_iso(),
            actor=actor,
            actor_type=actor_type,
            step=step,
            detail=detail or {},
        )
        try:
            # condition ensures we never overwrite an existing (claim_id, seq).
            self._table.put_item(
                Item=entry.to_dict(),
                ConditionExpression="attribute_not_exists(seq)",
            )
        except Exception as exc:
            return err(StorageError(f"Failed to append audit entry: {exc}"))
        return ok(entry)

    def get_trail(self, claim_id: str) -> Result:
        """Return the ordered audit trail for a claim (US-11)."""
        try:
            response = self._table.query(
                KeyConditionExpression=Key("claim_id").eq(claim_id),
                ScanIndexForward=True,  # ascending seq -> chronological
            )
        except Exception as exc:
            return err(StorageError(f"Failed to read audit trail: {exc}"))
        entries = [AuditEntry.from_dict(i) for i in response.get("Items", [])]
        return ok(entries)
