"""KB Client: managed RAG via Bedrock RetrieveAndGenerate (Q2:B).

Retrieves top-5 policy passages and generates a structured response in one call.
The bedrock-agent-runtime client is injectable for offline verification.
"""

from __future__ import annotations

import os

import boto3

from clairo_shared.errors import StorageError
from clairo_shared.result import Result, err, ok

from .types import RetrievalResult, RetrievedPassage, WEAK_MATCH_THRESHOLD

_TOP_K = 5


class KbClient:
    def __init__(self, agent_runtime_client=None, kb_id: str = None, model_arn: str = None):
        self._client = agent_runtime_client or boto3.client(
            "bedrock-agent-runtime",
            region_name=os.environ.get("AWS_REGION", "us-east-1"),
        )
        self._kb_id = kb_id or os.environ.get("KB_ID", "")
        self._model_arn = model_arn or os.environ.get(
            "BEDROCK_MODEL_ID", "anthropic.claude-3-5-sonnet-20240620-v1:0"
        )

    def retrieve_and_generate(self, query: str, prompt_instructions: str) -> Result:
        """Run managed RAG. Returns (RetrievalResult, None) or (None, StorageError)."""
        try:
            response = self._client.retrieve_and_generate(
                input={"text": f"{prompt_instructions}\n\nClaim:\n{query}"},
                retrieveAndGenerateConfiguration={
                    "type": "KNOWLEDGE_BASE",
                    "knowledgeBaseConfiguration": {
                        "knowledgeBaseId": self._kb_id,
                        "modelArn": self._model_arn,
                        "retrievalConfiguration": {
                            "vectorSearchConfiguration": {"numberOfResults": _TOP_K}
                        },
                    },
                },
            )
        except Exception as exc:
            return err(StorageError(f"RetrieveAndGenerate failed: {exc}"))

        generated = response.get("output", {}).get("text", "")
        passages = self._extract_citations(response)
        weak = self._is_weak(passages)
        return ok(RetrievalResult(generated_text=generated, passages=passages, weak=weak))

    @staticmethod
    def _extract_citations(response: dict) -> list:
        passages = []
        for citation in response.get("citations", []):
            for ref in citation.get("retrievedReferences", []):
                content = ref.get("content", {}).get("text", "")
                location = ref.get("location", {})
                source_id = (
                    location.get("s3Location", {}).get("uri")
                    or ref.get("metadata", {}).get("source", "")
                    or "unknown"
                )
                score = ref.get("metadata", {}).get("score", 0.0)
                passages.append(
                    RetrievedPassage(source_id=source_id, excerpt=content, score=float(score or 0.0))
                )
        return passages

    @staticmethod
    def _is_weak(passages: list) -> bool:
        """Weak when no passages, or all scores below the hardcoded threshold."""
        if not passages:
            return True
        return all(p.score < WEAK_MATCH_THRESHOLD for p in passages)
