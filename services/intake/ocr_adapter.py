"""OCR Adapter: extracts text + positional data via Amazon Textract (IR-1, Q5:A).

Uses synchronous Textract APIs (NFR-U2-3). boto3 client is injectable for
isolation and offline verification.
"""

from __future__ import annotations

import os

import boto3

from clairo_shared.errors import StorageError
from clairo_shared.models import DocumentRef
from clairo_shared.result import Result, err, ok

from .extraction import ExtractedBlock, ExtractedText


class OcrAdapter:
    def __init__(self, textract_client=None):
        self._textract = textract_client or boto3.client(
            "textract", region_name=os.environ.get("AWS_REGION", "us-east-1")
        )

    def extract(self, ref: DocumentRef) -> Result:
        """Run Textract on an S3 document. Returns (ExtractedText, None) or error."""
        try:
            response = self._textract.detect_document_text(
                Document={"S3Object": {"Bucket": ref.bucket, "Name": ref.key}}
            )
        except Exception as exc:
            return err(StorageError(f"Textract failed: {exc}"))

        blocks = []
        for item in response.get("Blocks", []):
            if item.get("BlockType") != "LINE":
                continue
            geometry = item.get("Geometry", {}).get("BoundingBox", {})
            bbox = [
                geometry.get("Left", 0.0),
                geometry.get("Top", 0.0),
                geometry.get("Width", 0.0),
                geometry.get("Height", 0.0),
            ]
            blocks.append(
                ExtractedBlock(
                    text=item.get("Text", ""),
                    page=item.get("Page", 1),
                    bbox=bbox,
                )
            )
        return ok(ExtractedText(blocks=blocks, source_ref=ref))
