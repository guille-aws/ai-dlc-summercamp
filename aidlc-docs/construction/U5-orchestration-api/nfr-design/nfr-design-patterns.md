# CLAIRO U5 Orchestration/API - NFR Design Patterns

No open NFR design questions — patterns follow from U5 FD and NFR requirements.

## Event-Driven Chaining (DynamoDB Streams)
- The Claims table stream delivers status-change records to the orchestrator Lambda.
- The orchestrator maps new status → next agent and async-invokes it (Lambda Event invocation).
- Idempotency: the orchestrator only acts on valid transitions (OR-4) and treats already-advanced claims as no-ops, tolerating duplicate/at-least-once stream delivery.

## Async Non-Blocking API
- The API handler performs quick DynamoDB/SSM operations and returns immediately; heavy agent work happens off-request via the stream-driven pipeline.

## Durable Pause/Resume
- Pause = claim status PendingReview persisted in DynamoDB. Resume = review API call finalizes the claim. No in-memory wait state; resilient to Lambda lifecycle.

## Role-Based Authorization at the Edge + Handler
- API Gateway Cognito authorizer authenticates; the handler enforces per-endpoint roles via clairo_shared.auth (require_role/require_any_role), returning 403 on failure.

## Result-Tuple Error Handling & Retries
- Handlers use result tuples; boto3 default retries for transient errors.

## Sizing
- API handler 512 MB / 30 s; orchestrator 512 MB / 1 min.
