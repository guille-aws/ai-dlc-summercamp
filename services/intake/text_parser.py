"""Email/Text Parser: extracts text blocks from email/text documents (IR-2).

Reads the document bytes from S3 (via injected DocumentStore) and produces
ExtractedText. Email bodies are parsed to plain text.
"""

from __future__ import annotations

from email import message_from_bytes

from clairo_shared.models import DocumentRef
from clairo_shared.result import Result, err, ok

from .extraction import ExtractedBlock, ExtractedText


class TextParser:
    def __init__(self, document_store):
        self._docs = document_store

    def parse(self, ref: DocumentRef) -> Result:
        """Return (ExtractedText, None) or (None, error)."""
        data, error = self._docs.get_document(ref)
        if error:
            return err(error)

        text = self._extract_text(data, ref.content_type)
        blocks = [
            ExtractedBlock(text=line, page=1)
            for line in text.splitlines()
            if line.strip()
        ]
        return ok(ExtractedText(blocks=blocks, source_ref=ref))

    @staticmethod
    def _extract_text(data: bytes, content_type: str) -> str:
        if (content_type or "").lower() == "message/rfc822":
            msg = message_from_bytes(data)
            parts = []
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        payload = part.get_payload(decode=True)
                        if payload:
                            parts.append(payload.decode("utf-8", errors="replace"))
            else:
                payload = msg.get_payload(decode=True)
                if payload:
                    parts.append(payload.decode("utf-8", errors="replace"))
            return "\n".join(parts)
        return data.decode("utf-8", errors="replace")
