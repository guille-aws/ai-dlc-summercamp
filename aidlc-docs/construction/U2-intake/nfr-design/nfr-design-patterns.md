# CLAIRO U2 Intake - NFR Design Patterns

No open NFR design questions — patterns are determined by U2 functional design and NFR requirements. Documented below for implementation.

## Asynchronous Processing Pattern
- Intake is invoked out-of-band (orchestrator invoke or S3-upload EventBridge event), not inline with the submission API request.
- The submission API persists a claim (status `Received`) and returns claim_id immediately; intake proceeds asynchronously (NFR-U2-1).

## Adapter Pattern (input routing)
- OCR Adapter and Email/Text Parser share a common `Extractor` interface returning `ExtractedText`.
- The handler selects the adapter by document content_type (IR-1/IR-2), keeping extractors independent and swappable.

## Structured-Output Prompt Pattern
- LLM Extractor issues a single Bedrock prompt requesting canonical claim JSON; response is parsed and defensively validated before mapping.
- Malformed LLM output → treated as unreadable → claim `Rejected` (IR-8).

## Result-Tuple Error Handling (inherited from U1)
- Each stage (extract, LLM, normalize, persist) returns `(value, error)`; the handler short-circuits on first error, setting `Rejected` (validation) or `Failed` (unrecoverable).

## Transient Fault Pattern
- boto3 standard retry mode for Textract/Bedrock/DynamoDB/S3 (NFR-U2-6). No custom retry wrapper for MVP.

## Idempotency Consideration
- Intake keys work on `claim_id`; re-processing the same claim overwrites the same record deterministically (safe for event redelivery at MVP level).

## Sizing
- Intake Lambda: 1024 MB / 5 min (NFR-U2-5) — overrides U0 default; applied in U2 infra/code.
