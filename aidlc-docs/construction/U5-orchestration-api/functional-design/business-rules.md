# CLAIRO U5 Orchestration/API - Business Rules

## Orchestration (async chaining, Q1:B)
- **OR-1**: Pipeline advancement is driven by claim status changes delivered via DynamoDB Streams; the orchestrator async-invokes the next stage.
- **OR-2**: Status → next-stage mapping: Received→Intake, IntakeComplete→Adjudication, Adjudicated→Compliance, ComplianceChecked→Routing.
- **OR-3**: Terminal statuses (Decided, Rejected, Failed) trigger no further stage invocation.
- **OR-4**: The orchestrator only acts on valid transitions (uses clairo_shared.rules); unexpected transitions are logged/audited and ignored.

## Routing (US-06, US-10)
- **OR-5**: Threshold is read from ConfigProvider at routing time (per-claim fresh, no cache).
- **OR-6**: route=auto when confidence >= threshold AND outcome != needs_more_info; else route=human.
- **OR-7**: needs_more_info always routes to human.
- **OR-8**: auto → finalize status Decided; human → status PendingReview.

## Finalization (Q4:A)
- **OR-9**: On auto-adjudicate, the final decision equals the adjudication outcome; compliance findings are attached as annotations (never override, per CR-4).
- **OR-10**: On human review, the final decision equals the reviewer's decision.

## Human Review (US-07)
- **OR-11**: Only Reviewer or Supervisor may submit a review (auth enforced, BR-16).
- **OR-12**: A review submission records reviewer identity + timestamp in the audit trail (FR-4.4).
- **OR-13**: If the reviewer's outcome differs from the recommendation, is_override=true and a ClaimOverridden event is emitted (Q5:A → U6).
- **OR-14**: Submitting a review on a non-PendingReview claim is rejected.

## API Authorization (US-12, Q6:A)
- **OR-15**: All endpoints require Cognito authentication; the handler enforces per-endpoint roles via clairo_shared.auth.
- **OR-16**: Submitter may create claims and read only their own claims.
- **OR-17**: Supervisor-only: update threshold (US-10), read audit trail (US-11).

## Auditing
- **OR-18**: Every routing decision, finalization, and human action appends an audit entry.
