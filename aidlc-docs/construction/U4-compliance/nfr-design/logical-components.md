# CLAIRO U4 Compliance - Logical Components

| Logical Component | Module (planned) | Patterns Applied |
|---|---|---|
| Compliance Handler | `services/compliance/handler.py` | Async; result-tuple orchestration; status transition; audit; annotate-only |
| GDPR Validator | `services/compliance/gdpr_validator.py` | Externalized rules (SSM→S3); LLM eval; defensive parse; injectable client |
| Explanation Generator | `services/compliance/explanation.py` | Dual-artifact (JSON + Markdown) to S3 |

## Infrastructure Interaction
- No new infra beyond U0: Bedrock model, S3 (rules read + explanations write), SSM (gdpr ref), DynamoDB claims, DynamoDB audit.
- Compliance Lambda role (U0 agents stack) grants Bedrock invoke, S3 RW, SSM read, DynamoDB claims RW, Audit PutItem. Sizing → 1024/5min. (SSM read grant to be added in U4 code-gen CDK update.)

## Non-Goals (MVP)
- Deterministic rule engine (using pure LLM per FD).
- Compliance-driven outcome override (annotate-only).
