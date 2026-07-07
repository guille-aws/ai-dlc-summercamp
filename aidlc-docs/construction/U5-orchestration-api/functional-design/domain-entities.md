# CLAIRO U5 Orchestration/API - Domain Entities

U5 reuses `clairo_shared` models (CanonicalClaim, PreliminaryDecision, ComplianceFindings, ReviewerDecision, Principal, ClaimStatus, DecisionOutcome). It adds orchestration/API working types.

## Working Types

### RoutingDecision
| Field | Type | Notes |
|---|---|---|
| route | str | "auto" or "human" |
| threshold_used | float | threshold at decision time |

### ReviewTask (a view over the claim record, Q3:A)
| Field | Type | Notes |
|---|---|---|
| claim_id | str | |
| recommendation | DecisionOutcome | adjudication outcome |
| confidence | float | |
| reasoning_chain | list[str] | |
| highlighted_evidence | list[dict] | page + bbox from evidence_refs |
| status | ClaimStatus | PendingReview |

*(Review tasks are not a separate entity/table — they are claims with status=PendingReview, listed via the status GSI.)*

### ApiRequestContext
| Field | Type | Notes |
|---|---|---|
| principal | Principal | from Cognito claims (clairo_shared.auth) |
| path | str | route |
| method | str | HTTP method |

## Pipeline Event (async chaining, Q1:B)
Realized via **DynamoDB Streams** on the Claims table:
- A claim `status` change emits a stream record.
- The orchestrator consumes it and async-invokes the next stage.

| status (new) | next action |
|---|---|
| Received | invoke Intake (or intake already running from upload) |
| IntakeComplete | invoke Adjudication |
| Adjudicated | invoke Compliance |
| ComplianceChecked | run Routing (auto → Decided; human → PendingReview) |
| Decided | terminal (emit ClaimOverridden earlier if override) |
