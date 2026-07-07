# CLAIRO U5 Orchestration/API - Tech Stack Decisions

| Concern | Decision | Rationale |
|---|---|---|
| Runtime | Python 3.12 Lambda | Platform consistency |
| Lambda split | Two Lambdas: API handler + orchestrator (Q1:A) | Separation of concerns; different triggers |
| API sizing | 512 MB / 30 s (Q2:A) | Lightweight request/response |
| Orchestrator sizing | 512 MB / 1 min (Q3:A) | Stream read + async invoke only |
| Chaining | DynamoDB Streams on Claims table → orchestrator | Realizes async chaining (FD Q1:B) without changing agents |
| API auth | API Gateway Cognito authorizer + handler role checks (Q6:A) | US-12 |
| Override event | EventBridge ClaimOverridden (source clairo.review) | FD Q5:A → U6 |
| Shared code | `clairo_shared` | Reuse |
| Unit tests | None (Q4:A) | Integration testing later |

## Dependencies
- `boto3` (DynamoDB, Lambda invoke, EventBridge, SSM).
- `clairo_shared` (bundled).

## CDK Changes (U5 code-gen)
- Add API handler wiring: the existing `api_stack.py` ApiOrchestratorFn becomes the API handler with the real `services/orchestration_api` asset; ensure invoke permissions for intake.
- Add an **orchestrator Lambda** consuming DynamoDB Streams from the Claims table; grant invoke on adjudication/compliance + EventBridge put.
- Enable a stream on the Claims table (`data_stack.py`).

## Module Layout (Code Generation)
```
services/orchestration_api/
├── api_handler.py       # API Gateway entry; routes; auth; create claim; reviews; audit; threshold
├── orchestrator.py      # DynamoDB Streams entry; advance pipeline by status
├── routing.py           # RoutingEvaluator
├── review.py            # ReviewTaskManager + EvidenceHighlighter
└── requirements.txt
```
