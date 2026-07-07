# CLAIRO U6 Feedback - Business Rules

## Trigger
- **FR6-1**: U6 runs only on an EventBridge `ClaimOverridden` event (source clairo.review) emitted by U5 on a human override (Q3:A, US-08).

## Corrective Example
- **FR6-2**: The corrective example contains the claim summary, the final (overridden) decision, and the reviewer rationale (Q1:A).
- **FR6-3**: The example is written to the kb-source S3 bucket at a deterministic key `corrective/{claim_id}.md` (Q4:A) — re-processing the same claim overwrites, avoiding duplicates.

## Knowledge Base Write
- **FR6-4**: After writing the S3 document, U6 triggers a Bedrock KB ingestion job so the example becomes retrievable (Q2:A, FR-5.1 automatic).
- **FR6-5**: KB write access is exclusive to U6 (per Q4:A design; enforced by IAM in U0).

## Reliability & Auditing
- **FR6-6**: Failures (S3/ingestion) are best-effort — logged and audited but do not affect the finalized claim.
- **FR6-7**: Every feedback write-back appends an audit entry (FR-5.3) including the s3_key and ingestion result.

## Effect
- **FR6-8**: Subsequent similar claims can retrieve the corrective example via normal adjudication RAG (no special weighting, U3 AR-3), realizing continuous improvement (US-08).
