# CLAIRO U6 Feedback - Infrastructure Design

**Summary**: No new AWS resource types. U6 runs on the feedback Lambda declared in U0's `agents_stack.py` and triggered by the existing EventBridge `ClaimOverridden` rule (U0 events stack). Changes applied during Code Generation:
1. **Handler asset**: replace inline placeholder with the real `services/feedback/` bundle (+ `clairo_shared`).
2. **IAM**: add `bedrock:StartIngestionJob` (KB write side); kb-source S3 write already granted.
3. **Env**: add KB_ID + KB_DATA_SOURCE_ID for ingestion.

No infra questions required — resources already decided in U0.

## Component → Infrastructure Mapping
| U6 Component | Infrastructure (U0) | Access |
|---|---|---|
| Feedback Handler (Lambda) | `clairo-dev-feedback` | executes (EventBridge-triggered) |
| Corrective example write | S3 `kb-source` bucket | write |
| KB ingestion | Bedrock Knowledge Base | StartIngestionJob (write) |
| Claim read | DynamoDB `clairo-dev-claims` | read |
| Audit | DynamoDB `clairo-dev-audit` | PutItem only |
| Trigger | EventBridge rule `override-feedback` (source clairo.review) | consumes |

## IAM (U0 agents stack, feedback role) — additions in U6 code-gen
- Existing: kb-source RW, Audit PutItem, KB write actions.
- **Add/confirm**: `bedrock:StartIngestionJob` on the KB; DynamoDB claims read.

## Changes to Apply in Code Generation
- `agents_stack.py`: feedback → `_make_service_function("feedback", ...)` (512/2min default is fine for a thin unit); add StartIngestionJob grant + claims read; add KB_ID/KB_DATA_SOURCE_ID env.
- Extend `build_lambdas.sh` SERVICES to include `feedback`.
- The EventBridge `override-feedback` rule already targets the feedback Lambda (U0 events stack) — no change needed.
