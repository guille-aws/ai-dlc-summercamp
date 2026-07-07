# CLAIRO U5 Orchestration/API - Code Summary

## Generated Files (workspace root)
```
services/orchestration_api/
├── requirements.txt
├── __init__.py
├── routing.py          # RoutingEvaluator (auto vs human; needs_more_info->human)
├── review.py           # ReviewTaskManager + evidence highlighting + override event
├── orchestrator.py     # DynamoDB Streams consumer: status -> async-invoke next agent; routing
└── api_handler.py      # API Gateway entry: 6 role-scoped endpoints; Cognito principal + role checks

infra/stacks/data_stack.py     # UPDATED: Claims table stream (NEW_AND_OLD_IMAGES)
infra/stacks/api_stack.py      # UPDATED: API handler real asset (512/30s) + orchestrator Lambda (512/1min) w/ stream event source
libs/clairo_shared/.../claim_repository.py  # UPDATED: added get_result() accessor
scripts/build_lambdas.sh       # UPDATED: SERVICES includes orchestration_api
```

## Decisions Applied
- Two Lambdas: API handler + orchestrator (stream consumer).
- Async chaining via DynamoDB Streams: Received→Intake, IntakeComplete→Adjudication, Adjudicated→Compliance, ComplianceChecked→Routing.
- Routing reads threshold fresh; auto→Decided (adjudication outcome), else PendingReview; needs_more_info→human.
- Review tasks = claims with status=PendingReview (status GSI). Override → EventBridge ClaimOverridden → U6.
- Cognito authorizer + per-endpoint role checks (Submitter/Reviewer/Supervisor).
- 512/30s API, 512/1min orchestrator; result tuples; no unit tests.

## Verification Performed
- Ran `scripts/build_lambdas.sh` (vendors clairo_shared into all 4 services).
- Offline logic checks (fake clients): routing (auto/human/needs_more_info), review submit + override event emission, review-on-non-pending rejection, API role authz (reviewer 403 / supervisor 200 for threshold) — all passed.
- `cdk synth`: 9 stacks synthesize; Claims table stream enabled; orchestrator event-source mapping present; orchestration_api asset bundles both handlers + clairo_shared.

## Deployment Prerequisites
- Run `bash scripts/build_lambdas.sh` before `cdk deploy`.
- Seed data: Bedrock KB (policy docs) + GDPR policy doc at `gdpr_rules_ref` (Build & Test).

## First Deployable End-to-End Slice
- Pipeline is now wired end-to-end. Submit a synthetic claim via `POST /claims` (or S3 upload) → Intake→Adjudication→Compliance→Routing; low-confidence claims appear in `GET /reviews`; overrides feed the (placeholder until U6) feedback path via EventBridge.

## Notes
- No unit tests (NFR Q4:A); integration testing in Build & Test.
- U6 Feedback remains an inline placeholder until generated.
