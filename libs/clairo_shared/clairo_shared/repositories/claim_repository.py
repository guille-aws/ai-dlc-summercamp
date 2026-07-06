"""Claim Repository: DynamoDB access for the single claim record (Q3:A).

Uses an injectable boto3 DynamoDB resource for isolation (NFR design DI pattern).
boto3 default retry mode handles transient faults (Q1:A). Returns result tuples.
"""

from __future__ import annotations

import os
from typing import Optional

import boto3

from ..errors import NotFoundError, StorageError
from ..models import CanonicalClaim, ClaimStatus
from ..result import Result, err, ok
from ..util import now_iso


class ClaimRepository:
    def __init__(self, table_name: Optional[str] = None, dynamodb_resource=None):
        self._table_name = table_name or os.environ.get("CLAIMS_TABLE", "clairo-dev-claims")
        self._dynamodb = dynamodb_resource or boto3.resource("dynamodb")
        self._table = self._dynamodb.Table(self._table_name)

    def create_claim(self, claim: CanonicalClaim) -> Result:
        """Persist a new claim record. Returns (claim_id, None) or (None, StorageError)."""
        ts = now_iso()
        claim.created_at = claim.created_at or ts
        claim.updated_at = ts
        try:
            self._table.put_item(Item=claim.to_dict())
        except Exception as exc:  # boto3 client errors
            return err(StorageError(f"Failed to create claim: {exc}"))
        return ok(claim.claim_id)

    def get_claim(self, claim_id: str) -> Result:
        """Fetch a claim. Returns (CanonicalClaim, None) or (None, NotFoundError/StorageError)."""
        try:
            response = self._table.get_item(Key={"claim_id": claim_id})
        except Exception as exc:
            return err(StorageError(f"Failed to get claim: {exc}"))
        item = response.get("Item")
        if not item:
            return err(NotFoundError(f"Claim not found: {claim_id}"))
        return ok(CanonicalClaim.from_dict(item))

    def update_status(self, claim_id: str, status: ClaimStatus) -> Result:
        """Update the claim status and updated_at timestamp."""
        try:
            self._table.update_item(
                Key={"claim_id": claim_id},
                UpdateExpression="SET #s = :s, updated_at = :u",
                ExpressionAttributeNames={"#s": "status"},
                ExpressionAttributeValues={":s": status.value, ":u": now_iso()},
            )
        except Exception as exc:
            return err(StorageError(f"Failed to update status: {exc}"))
        return ok(status)

    def update_result(self, claim_id: str, stage: str, result_data: dict) -> Result:
        """Store a per-stage result attribute on the single claim record."""
        attr = f"{stage}_result"
        try:
            self._table.update_item(
                Key={"claim_id": claim_id},
                UpdateExpression="SET #a = :r, updated_at = :u",
                ExpressionAttributeNames={"#a": attr},
                ExpressionAttributeValues={":r": result_data, ":u": now_iso()},
            )
        except Exception as exc:
            return err(StorageError(f"Failed to update result: {exc}"))
        return ok(attr)

    def list_by_status(self, status: ClaimStatus, limit: int = 50) -> Result:
        """List claims in a given status via the status GSI (review queue support)."""
        try:
            response = self._table.query(
                IndexName="status-index",
                KeyConditionExpression=boto3.dynamodb.conditions.Key("status").eq(
                    status.value
                ),
                Limit=limit,
            )
        except Exception as exc:
            return err(StorageError(f"Failed to list by status: {exc}"))
        items = [CanonicalClaim.from_dict(i) for i in response.get("Items", [])]
        return ok(items)
