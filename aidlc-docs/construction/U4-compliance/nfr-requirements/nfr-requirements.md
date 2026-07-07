# CLAIRO U4 Compliance - NFR Requirements

> Extensions OFF. MVP defaults only.

## Performance
- **NFR-U4-1**: Compliance runs asynchronously as a pipeline step after adjudication.
- **NFR-U4-2**: One LLM evaluation call + explanation generation per claim.

## Processing Model
- **NFR-U4-3**: GDPR policy text is loaded per invocation: read SSM `gdpr_rules_ref` (S3 URI) → load doc from S3 (Q2:A). Always reflects latest published rules (NFR-6.2).
- **NFR-U4-4**: Pure LLM evaluation against the rules text (FD Q2:B).

## Capacity / Sizing
- **NFR-U4-5**: Compliance Lambda sized 1024 MB / 5 min (Q1:A). Overrides U0 default; applied in U4 infra/code.

## Reliability
- **NFR-U4-6**: boto3 default retries.
- **NFR-U4-7**: Unloadable rules → Failed; unusable LLM output → conservative findings without blocking pipeline (CR-11).

## Observability
- **NFR-U4-8**: CloudWatch logs + error/throttle alarms (U0).

## Testing
- **NFR-U4-9**: No U4 unit tests (Q3:A); integration testing in Build & Test.

## Security (defaults)
- **NFR-U4-10**: Least-privilege IAM — Bedrock invoke, S3 read (rules) + write (explanations), SSM read (gdpr ref), DynamoDB claims RW, Audit PutItem. Synthetic data only.
