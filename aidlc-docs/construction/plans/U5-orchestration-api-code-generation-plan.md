# CLAIRO U5 Orchestration/API - Code Generation Plan

**Unit**: U5 (orchestrator + Claim API + HITL backend)
**Code location**: `services/orchestration_api/`
**Depends on**: U1 (`clairo_shared`), U2/U3/U4 (agent Lambdas), U0 (API GW, DynamoDB, EventBridge, Cognito).
**Stories**: US-01, US-06, US-07, US-09, US-10, US-11.

## Decisions Applied
- Two Lambdas (API handler + orchestrator); DynamoDB Streams chaining; status-GSI review tasks; auto→Decided with adjudication outcome + compliance annotations; override→EventBridge; Cognito + handler role checks; 512/30s API, 512/1min orchestrator; result tuples; no unit tests.

## Generation Steps

- [x] **Step 1: Scaffolding** — `requirements.txt`, `__init__.py`.
- [x] **Step 2: Routing** — `routing.py`.
- [x] **Step 3: Review** — `review.py` (+ evidence highlighting, override event).
- [x] **Step 4: Orchestrator** — `orchestrator.py` (Streams consumer; +get_result accessor in shared repo).
- [x] **Step 5: API Handler** — `api_handler.py` (6 endpoints, role checks).
- [x] **Step 6: CDK update** — Claims stream; API handler asset (512/30s) + orchestrator Lambda (512/1min) w/ stream source; build_lambdas.sh extended.
- [x] **Step 7: Verify** — build_lambdas OK; offline logic checks passed; cdk synth passed (9 stacks, stream + event-source mapping, asset bundles clairo_shared).
- [x] **Step 8: Documentation** — `aidlc-docs/construction/U5-orchestration-api/code/README.md`.

## Notes
- Injectable clients for offline verification (DynamoDB/Lambda/EventBridge/SSM fakes).
- No unit tests (NFR Q4:A); verify via logic checks + synth here, integration in Build & Test.
