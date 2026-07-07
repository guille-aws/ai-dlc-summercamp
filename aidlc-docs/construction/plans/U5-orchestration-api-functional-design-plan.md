# CLAIRO U5 HITL/API/Orchestration - Functional Design Plan

**Unit**: U5 (serverless: orchestrator + Claim API + HITL review backend)
**Responsibility**: Claim Orchestrator (drives Intake→Adjudication→Compliance→Routing, hybrid + pause/async), Routing Evaluator, Review Task Manager, Evidence Highlighter, and the role-scoped Claim API.
**Stories**: US-01, US-06, US-07, US-09, US-10, US-11.
**Depends on**: U1 (`clairo_shared`), U2/U3/U4 (agent Lambdas), U0 (API GW, Lambdas, EventBridge, Cognito).

Technology-agnostic business logic design. Concrete code in Code Generation.

---

## Part A: Functional Design Questions

Answer each with the letter after `[Answer]:`. Choose **X) Other** if none fit. Let me know when done.

### Question 1: Orchestrator Invocation of Agents
How should the orchestrator invoke the Intake/Adjudication/Compliance Lambdas?

A) Synchronous Lambda invoke (RequestResponse) in sequence within the orchestrator Lambda

B) Asynchronous chaining (each stage invokes the next via events)

X) Other (please describe after [Answer]: tag below)

[Answer]: B) Asynchronous chaining (each stage invokes the next via events)

### Question 2: Pause/Resume Mechanism for HITL
How should the "Pending Review" pause + later resume work (Q6:A pause/async)?

A) Orchestrator stops after routing=human; a separate resume path (triggered by the review API) runs finalization — state tracked via claim status + a review task record

B) Step Functions-style wait token

X) Other (please describe after [Answer]: tag below)

[Answer]: A) Orchestrator stops after routing=human; a separate resume path (triggered by the review API) runs finalization — state tracked via claim status + a review task record

### Question 3: Review Task Storage
Where should review tasks live?

A) As claim records queried by status=PendingReview (via the status GSI) — no separate table

B) A dedicated review-tasks DynamoDB table

X) Other (please describe after [Answer]: tag below)

[Answer]: A) As claim records queried by status=PendingReview (via the status GSI) — no separate table

### Question 4: Finalization on Auto-Adjudicate
When confidence ≥ threshold (auto), what is the final status and decision source?

A) Status Decided; final decision = adjudication outcome (compliance annotations attached)

B) Status Decided only after a no-op review acknowledgment

X) Other (please describe after [Answer]: tag below)

[Answer]: A) Status Decided; final decision = adjudication outcome (compliance annotations attached)

### Question 5: Override Event Emission
When a reviewer overrides, how is the feedback loop (U6) triggered?

A) Orchestrator/review handler emits an EventBridge "ClaimOverridden" event (source clairo.review) → U6

B) Direct synchronous invoke of the feedback Lambda

X) Other (please describe after [Answer]: tag below)

[Answer]: A) Orchestrator/review handler emits an EventBridge "ClaimOverridden" event (source clairo.review) → U6

### Question 6: API Authorization Enforcement
How are role restrictions (US-12) enforced at the API?

A) Cognito authorizer authenticates; the handler checks the caller's group/role per endpoint using clairo_shared.auth

B) Separate API Gateway authorizers per role

X) Other (please describe after [Answer]: tag below)

[Answer]: A) Cognito authorizer authenticates; the handler checks the caller's group/role per endpoint using clairo_shared.auth

---

## Part B: Execution Checklist (executed after plan approval)

- [x] Generate `aidlc-docs/construction/U5-orchestration-api/functional-design/business-logic-model.md`
- [x] Generate `aidlc-docs/construction/U5-orchestration-api/functional-design/business-rules.md`
- [x] Generate `aidlc-docs/construction/U5-orchestration-api/functional-design/domain-entities.md`
- [x] Update aidlc-state.md and audit.md
