# CLAIRO - Unit of Work Dependencies

## Dependency Matrix

| Unit | Depends On | Reason |
|---|---|---|
| U0 Infrastructure | (none) | Defines all AWS resources; provisioned first |
| U1 Shared Platform | U0 | Uses DynamoDB, S3, audit store, Cognito, config provisioned by infra |
| U2 Intake | U1, U0 | Uses shared schema/repos/audit; Textract + Bedrock + S3 |
| U3 Adjudication | U1, U0 | Uses shared repos/audit; reads Bedrock KB |
| U4 Compliance | U1, U0 | Uses shared repos/audit/config; S3 for explanations |
| U5 HITL/Review+API+Orchestration | U1, U2, U3, U4, U0 | Orchestrates agents; serves API + review; uses shared platform |
| U6 Feedback | U1, U0 | Event-triggered; writes Bedrock KB; uses audit |
| U7 Web UI | U5 | Calls the Claim API (role-scoped); Cognito auth |

## Build / Delivery Sequence (Q5:A)
```
1. U0 Infrastructure   (foundational AWS resources)
2. U1 Shared Platform  (schema, repos, audit, config, auth)
3. U2 Intake  ┐
4. U3 Adjudication  ├─ agents (can be built in parallel after U1)
5. U4 Compliance  ┘
6. U5 HITL/Review + API + Orchestration  (integrates the agents)
7. U6 Feedback  (depends on override events from U5)
8. U7 Web UI    (depends on U5 API)
```

## Parallelization Opportunities
- After U1 is complete, U2/U3/U4 can be developed in parallel (independent agents).
- U7 (Web UI) can be scaffolded in parallel with U5 once the API contract is fixed.

## Communication Between Units
- **Synchronous**: U5 Orchestrator invokes U2 → U3 → U4 in sequence.
- **Event-driven**: S3 upload → U5 orchestrator start; override → event → U6 Feedback.
- **Shared data**: U1 provides the single claim record (DynamoDB), documents (S3), and audit trail consumed across units.

## Coordination Points
- **Canonical claim schema** (owned by U1) is the contract between U2 → U3 → U4.
- **Claim API contract** (owned by U5) is the contract for U7.
- **KB access**: U3 read-only, U6 write-only (enforced via IAM roles from U0).
