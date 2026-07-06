"""Document Store: S3 access for raw documents and explanation docs.

Injectable boto3 S3 client. Returns result tuples.
"""

from __future__ import annotations

import os
from typing import Optional

import boto3

from ..errors import NotFoundError, StorageError
from ..models import DocumentRef
from ..result import Result, err, ok


class DocumentStore:
    def __init__(self, bucket_name: Optional[str] = None, s3_client=None):
        self._bucket = bucket_name or os.environ.get(
            "DOCUMENTS_BUCKET", "clairo-dev-documents"
        )
        self._s3 = s3_client or boto3.client("s3")

    def put_document(
        self, data: bytes, key: str, content_type: str = "application/octet-stream"
    ) -> Result:
        """Store bytes at key. Returns (DocumentRef, None) or (None, StorageError)."""
        try:
            self._s3.put_object(
                Bucket=self._bucket, Key=key, Body=data, ContentType=content_type
            )
        except Exception as exc:
            return err(StorageError(f"Failed to put document: {exc}"))
        return ok(DocumentRef(bucket=self._bucket, key=key, content_type=content_type))

    def get_document(self, ref: DocumentRef) -> Result:
        """Fetch bytes for a DocumentRef. Returns (bytes, None) or (None, error)."""
        try:
            response = self._s3.get_object(Bucket=ref.bucket, Key=ref.key)
            return ok(response["Body"].read())
        except self._s3.exceptions.NoSuchKey:
            return err(NotFoundError(f"Document not found: {ref.key}"))
        except Exception as exc:
            return err(StorageError(f"Failed to get document: {exc}"))

    def put_explanation(self, claim_id: str, text: str) -> Result:
        """Store an audit-ready explanation doc under the explanations/ prefix."""
        key = f"explanations/{claim_id}.md"
        return self.put_document(text.encode("utf-8"), key, "text/markdown")
