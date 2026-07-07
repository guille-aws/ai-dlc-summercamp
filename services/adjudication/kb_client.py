"""KB Client: retrieves policy passages from the Bedrock Knowledge Base via the
`Retrieve` API (top-K), then the reasoner invokes the model separately. This
avoids RetrieveAndGenerate's managed-KB limitations.

The bedrock-agent-runtime client is injectable for offline verification.
"""

from __future__ import annotations

import os

import boto3

from clairo_shared.errors import StorageError
from clairo_shared.result import Result, err, ok

from types_ import RetrievalResult, RetrievedPassage, WEAK_MATCH_THRESHOLD

_TOP_K = 5


class KbClient:
    def __init__(self, agent_runtime_client=None, kb_id: str = None):
        self._client = agent_runtime_client or boto3.client(
            "bedrock-agent-runtime",
            region_name=os.environ.get("AWS_REGION", "us-east-1"),
        )
        self._kb_id = kb_id or os.environ.get("KB_ID", "")

    def retrieve(self, query: str) -> Result:
        """Retrieve top-K policy passages. Returns (RetrievalResult, None) or error."""
        try:
            # Managed knowledge bases do not accept vectorSearchConfiguration;
            # omit retrievalConfiguration and let the KB use its managed search.
            response = self._client.retrieve(
                knowledgeBaseId=self._kb_id,
                retrievalQuery={"text": query},
            )
        except Exception as exc:
            return err(StorageError(f"Retrieve failed: {exc}"))

        passages = []
        for item in response.get("retrievalResults", []):
            content = item.get("content", {}).get("text", "")
            location = item.get("location", {})
            source_id = (
                location.get("s3Location", {}).get("uri")
                or "unknown"
            )
            score = item.get("score", 0.0)
            passages.append(
                RetrievedPassage(source_id=source_id, excerpt=content, score=float(score or 0.0))
            )
        weak = self._is_weak(passages)
        return ok(RetrievalResult(generated_text="", passages=passages, weak=weak))

    @staticmethod
    def _is_weak(passages: list) -> bool:
        """Weak when no passages, or all scores below the hardcoded threshold."""
        if not passages:
            return True
        return all(p.score < WEAK_MATCH_THRESHOLD for p in passages)
