# CLAIRO U3 Adjudication - NFR Requirements

> Extensions OFF. MVP defaults only.

## Performance
- **NFR-U3-1**: Adjudication runs asynchronously as part of the pipeline; not inline with submission.
- **NFR-U3-2**: Single managed RAG call (RetrieveAndGenerate) reduces round-trips.

## Processing Model
- **NFR-U3-3**: KB access via Bedrock `RetrieveAndGenerate` (managed RAG, one call) (Q2:B). Structured output (outcome, self-assessed confidence, reasoning, citations) is requested via the prompt template; the response is defensively parsed.
- **NFR-U3-4**: Retrieval depth top-5 (from FD AR-1).

## Capacity / Sizing
- **NFR-U3-5**: Adjudication Lambda sized 1024 MB / 5 min (Q1:A). Overrides U0 default; updated in U3 infra/code.

## Reliability
- **NFR-U3-6**: boto3 default retries.
- **NFR-U3-7**: Weak retrieval → low-confidence decision (hardcoded weak-match threshold for MVP, Q3:B). Unusable output → low-confidence needs_more_info (AR-11).

## Observability
- **NFR-U3-8**: CloudWatch logs + error/throttle alarms (U0).

## Testing
- **NFR-U3-9**: No U3 unit tests (Q4:A); integration testing in Build & Test.

## Security (defaults)
- **NFR-U3-10**: Least-privilege IAM — Bedrock RetrieveAndGenerate/InvokeModel + KB read (no write), DynamoDB claims RW, Audit PutItem. Synthetic data only.
