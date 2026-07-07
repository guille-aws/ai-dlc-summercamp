# CLAIRO U5 Orchestration/API - NFR Requirements

> Extensions OFF. MVP defaults only.

## Architecture
- **NFR-U5-1**: Two Lambdas (Q1:A): an **API handler** (behind API Gateway) and an **orchestrator** (DynamoDB Streams consumer that async-invokes agents).

## Performance
- **NFR-U5-2**: API handler is lightweight request/response (no LLM work) → 512 MB / 30 s (Q2:A). Submission returns claim_id immediately (NFR-3.2).
- **NFR-U5-3**: Orchestrator just reads stream records and async-invokes the next agent → 512 MB / 1 min (Q3:A).

## Reliability
- **NFR-U5-4**: boto3 default retries. Orchestrator only acts on valid status transitions (OR-4); invalid/duplicate stream records are ignored idempotently.
- **NFR-U5-5**: Pause/resume state is durable in the claim record (status), so a reviewer can resume regardless of pipeline timing.

## Security
- **NFR-U5-6**: Cognito authorizer authenticates all endpoints; handler enforces per-endpoint roles via clairo_shared.auth (US-12). Least-privilege IAM: API handler needs DynamoDB claims RW + audit read/PutItem + SSM (threshold) + invoke intake; orchestrator needs claims read + invoke agents + EventBridge put (override).
- **NFR-U5-7**: Synthetic data only.

## Observability
- **NFR-U5-8**: CloudWatch logs for both Lambdas; error/throttle alarms (U0).

## Testing
- **NFR-U5-9**: No U5 unit tests (Q4:A); integration testing in Build & Test.
