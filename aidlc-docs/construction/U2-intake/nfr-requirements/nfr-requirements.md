# CLAIRO U2 Intake - NFR Requirements

> Security/Resiliency/PBT extensions OFF. MVP defaults only.

## Performance
- **NFR-U2-1**: Intake runs asynchronously (Q1:A) — the submission API returns immediately with a claim_id; OCR/LLM latency does not block the caller (satisfies NFR-3.2).
- **NFR-U2-2**: Straight-through intake targets completion within a few minutes under normal load (NFR-3.1).

## Processing Model
- **NFR-U2-3**: Textract uses synchronous APIs (AnalyzeDocument/DetectDocumentText) suitable for single-page/small documents (Q2:A). Large multi-page async Textract is a documented future extension.
- **NFR-U2-4**: Bedrock Claude Sonnet invoked synchronously within the intake Lambda.

## Capacity / Sizing
- **NFR-U2-5**: Intake Lambda sized at 1024 MB memory / 5 min timeout (Q3:B). **Note**: overrides the U0 default (512 MB / 2 min); to be reconciled in U2 infra/code generation.

## Reliability
- **NFR-U2-6**: boto3 default retries for transient Textract/Bedrock/AWS errors.
- **NFR-U2-7**: Unreadable input → `Rejected`; unrecoverable errors → `Failed` (per U2 business rules IR-8/IR-10).

## Observability
- **NFR-U2-8**: CloudWatch logs for the intake Lambda; error/throttle alarms (from U0 observability stack).

## Testing
- **NFR-U2-9**: No U2 unit tests (Q4:B); validated via integration testing in Build & Test.

## Security (defaults)
- **NFR-U2-10**: Least-privilege IAM (Textract, Bedrock invoke, S3 read/write documents, DynamoDB claims RW, Audit PutItem). Synthetic data only.
