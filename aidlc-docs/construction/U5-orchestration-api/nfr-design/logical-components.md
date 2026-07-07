# CLAIRO U5 Orchestration/API - Logical Components

| Logical Component | Module (planned) | Patterns Applied |
|---|---|---|
| API Handler | `services/orchestration_api/api_handler.py` | Async non-blocking API; role authz; result tuples |
| Orchestrator | `services/orchestration_api/orchestrator.py` | DynamoDB Streams consumer; idempotent transition-driven chaining |
| Routing Evaluator | `services/orchestration_api/routing.py` | Fresh threshold read; auto/human decision |
| Review Task Manager + Evidence Highlighter | `services/orchestration_api/review.py` | Status-GSI task listing; override event emission |

## Infrastructure Interaction
- **New**: DynamoDB Stream on Claims table; orchestrator Lambda as stream consumer.
- **Reused (U0)**: API Gateway + Cognito authorizer, API handler Lambda, EventBridge (override event), SSM (threshold), DynamoDB claims/audit.
- IAM: API handler → claims RW, audit read + PutItem, SSM get/put (threshold), invoke intake; orchestrator → claims read, invoke adjudication/compliance, EventBridge PutEvents.

## Non-Goals (MVP)
- Step Functions wait tokens (using durable status-based pause instead).
- Dedicated review-tasks table (using status GSI).
