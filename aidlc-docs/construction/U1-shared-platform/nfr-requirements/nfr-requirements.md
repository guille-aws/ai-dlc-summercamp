# CLAIRO U1 Shared Platform - NFR Requirements

> Security, Resiliency, and Property-Based Testing extension baselines are OFF. These NFRs are MVP-level defaults, not enforced extension rules.

## Performance
- **NFR-U1-1**: Repository operations are single-item DynamoDB calls (get/put/update) — sub-100ms typical; no heavy computation in the shared layer.
- **NFR-U1-2**: Config Provider reads SSM on every call (no caching, Q3:B) — always fresh threshold/rules; acceptable for MVP call volumes.

## Scalability
- **NFR-U1-3**: DynamoDB tables use PAY_PER_REQUEST (on-demand) — scales with load without capacity planning.
- **NFR-U1-4**: Shared library is stateless; concurrency scales with the consuming Lambdas.

## Availability / Reliability
- **NFR-U1-5**: Relies on managed AWS service availability (DynamoDB, S3, SSM); no custom HA design (resiliency ext OFF).
- **NFR-U1-6**: Error signaling uses result/error tuples (Q5:B) — callers explicitly handle failures; no uncaught exceptions escape shared APIs for expected error conditions.

## Security (defaults only; extension OFF)
- **NFR-U1-7**: Encryption at rest via AWS-managed keys (DynamoDB, S3).
- **NFR-U1-8**: Least-privilege IAM applied by consuming units; append-only audit enforced by IAM (PutItem only).
- **NFR-U1-9**: Synthetic/non-real data only (NFR-4.1). No PHI.

## Maintainability
- **NFR-U1-10**: AWS clients are injectable into repository/provider classes (Q2:A) for isolation and future testability.
- **NFR-U1-11**: Single shared library (`clairo_shared`) consumed by all units — one source of truth for schema and data access.

## Testing
- **NFR-U1-12**: No unit tests for U1 per user decision (Q4:X). Verification in the Build & Test phase relies on build/import checks and CDK synth. (Noted trade-off: reduced automated coverage for the shared layer.)
