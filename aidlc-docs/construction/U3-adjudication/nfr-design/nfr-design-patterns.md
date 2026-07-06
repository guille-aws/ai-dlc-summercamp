# CLAIRO U3 Adjudication - NFR Design Patterns

No open NFR design questions — patterns follow from U3 FD and NFR requirements.

## Managed RAG Pattern
- Single Bedrock `RetrieveAndGenerate` call performs retrieval (top-5) + generation.
- The generation prompt template instructs the model to return structured JSON: outcome, confidence (0.0–1.0), reasoning_chain, citations.

## Structured-Output + Defensive Parse
- The reasoner parses the model's text output as JSON, tolerating code fences / surrounding prose (reuse the defensive-parse approach from U2's extractor).
- Unusable output → low-confidence `needs_more_info` decision (AR-11) rather than a hard failure — ensures the claim still routes to a human.

## Confidence Clamping
- `confidence` is clamped to [0.0, 1.0] (AR-6) before persistence.

## Weak-Retrieval Handling
- If citations/scores are empty or below the hardcoded weak-match threshold, the decision is treated as weak-basis → low confidence, driving HITL routing downstream (AR-9, Q4:A from FD).

## Result-Tuple Error Handling & Retries
- Each step returns `(value, error)`; boto3 default retries for transient Bedrock/DynamoDB errors.
- Unrecoverable errors → claim `Failed`.

## Sizing
- Adjudication Lambda 1024 MB / 5 min (NFR-U3-5) — applied in U3 infra/code.
