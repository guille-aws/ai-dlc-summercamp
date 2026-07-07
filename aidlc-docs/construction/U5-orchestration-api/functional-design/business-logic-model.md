# CLAIRO U5 Orchestration/API - Business Logic Model

## Components

### 1. Claim Orchestrator (async chaining, Q1:B)
- Advances the pipeline based on claim status changes, delivered via **DynamoDB Streams** on the Claims table.
- On each relevant status transition, async-invokes the next agent Lambda (Event invocation type):
  - `Received` → Intake (unless intake already triggered by S3 upload)
  - `IntakeComplete` → Adjudication
  - `Adjudicated` → Compliance
  - `ComplianceChecked` → Routing Evaluator (final step, below)
- Rationale: async chaining keeps agents decoupled and avoids one long-running orchestrator invocation; agents (U2–U4) remain unchanged (they just update status).

### 2. Routing Evaluator
- Reads threshold from ConfigProvider; compares against adjudication confidence.
- `confidence >= threshold` AND outcome != needs_more_info → route=auto → finalize `Decided` (Q4:A: decision = adjudication outcome, compliance annotations attached).
- else → route=human → set status `PendingReview` and create the review task view.
- `needs_more_info` always routes to human (BR-15).

### 3. Review Task Manager
- `list_tasks()`: query claims with status=PendingReview via status GSI (Q3:A).
- `get_task(claim_id)`: assemble ReviewTask (recommendation, confidence, reasoning, highlighted evidence).
- `submit_review(claim_id, ReviewerDecision)`: record decision + reviewer identity/timestamp (audit), finalize `Decided`; if override, emit ClaimOverridden event (Q5:A).

### 4. Evidence Highlighter
- Builds highlighted_evidence from the claim's evidence_refs (page + bbox) for reviewer display (US-06).

### 5. Claim API (role-scoped, Q6:A)
- Cognito authorizer authenticates; handler enforces role per endpoint via `clairo_shared.auth.require_role`/`require_any_role`.
- Endpoints:
  - `POST /claims` (Submitter): create claim (status Received), store docs ref; returns claim_id (US-01).
  - `GET /claims/{id}` (any authenticated, own for submitter): status + decision + reasoning + explanation ref (US-09).
  - `GET /reviews` (Reviewer/Supervisor): list pending review tasks (US-06).
  - `POST /reviews/{claimId}` (Reviewer/Supervisor): submit decision/override (US-07).
  - `GET /claims/{id}/audit` (Supervisor): audit trail (US-11).
  - `PUT /config/threshold` (Supervisor): update confidence threshold (US-10).

## Resume / Pause (Q2:A)
- Pause: orchestrator stops at `PendingReview`; state is the claim record + status.
- Resume: `POST /reviews/{claimId}` finalizes the claim (`Decided`), independent of the pipeline stream.

## Interactions
- **U1 shared**: ClaimRepository, AuditLogger, ConfigProvider, DocumentStore, auth, models, rules.
- **U2–U4**: async-invoked agent Lambdas.
- **U6**: ClaimOverridden EventBridge event on override.
- **AWS**: API Gateway, DynamoDB Streams, Lambda, EventBridge, Cognito.
