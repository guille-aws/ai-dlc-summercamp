# CLAIRO U5 Orchestration/API - NFR Requirements Plan

**Unit**: U5 (orchestrator + Claim API + HITL backend)

**Already established**: Python 3.12; Lambda; API Gateway; Cognito authorizer; boto3 (injectable); `clairo_shared`; result tuples; async chaining via DynamoDB Streams; EventBridge override event; CloudWatch logs + basic alarms; extensions OFF; synthetic data.

Open U5-specific NFR questions below.

---

## Part A: NFR Questions

Answer each with the letter after `[Answer]:`. Choose **X) Other** if none fit. Let me know when done.

### Question 1: Lambda Handler Split
How should U5's Lambda functions be organized?

A) Two Lambdas — one API handler (behind API Gateway) + one orchestrator (DynamoDB Streams consumer)

B) A single Lambda handling both API events and stream events (dispatch by event type)

X) Other (please describe after [Answer]: tag below)

[Answer]: A) Two Lambdas — one API handler (behind API Gateway) + one orchestrator (DynamoDB Streams consumer)

### Question 2: API Lambda Sizing
Memory/timeout for the API handler (fast request/response)?

A) 512 MB / 30 s (API is lightweight; agents run async)

B) 1024 MB / 2 min

X) Other (please describe after [Answer]: tag below)

[Answer]: A) 512 MB / 30 s (API is lightweight; agents run async)


### Question 3: Orchestrator Lambda Sizing
Memory/timeout for the orchestrator (stream consumer that async-invokes agents)?

A) 512 MB / 1 min (just reads stream + invokes; agents do the heavy work)

B) 1024 MB / 5 min

X) Other (please describe after [Answer]: tag below)

[Answer]: A) 512 MB / 1 min (just reads stream + invokes; agents do the heavy work)

### Question 4: Unit Testing for U5
Testing approach for U5 (routing logic, auth checks, review submission)?

A) No unit tests (consistent with U1-U4); integration testing in Build & Test

B) pytest for routing/auth/review logic with mocked clients

X) Other (please describe after [Answer]: tag below)

[Answer]: A) No unit tests (consistent with U1-U4); integration testing in Build & Test

---

## Part B: Execution Checklist (executed after plan approval)

- [x] Generate `aidlc-docs/construction/U5-orchestration-api/nfr-requirements/nfr-requirements.md`
- [x] Generate `aidlc-docs/construction/U5-orchestration-api/nfr-requirements/tech-stack-decisions.md`
- [x] Update aidlc-state.md and audit.md
