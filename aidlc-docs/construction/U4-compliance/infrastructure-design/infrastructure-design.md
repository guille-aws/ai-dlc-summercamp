# CLAIRO U4 Compliance - Infrastructure Design

**Summary**: No new AWS resource types. U4 runs on the compliance Lambda declared in U0's `agents_stack.py`, with changes applied during Code Generation:
1. **Sizing**: compliance Lambda → 1024 MB / 5 min (NFR-U4-5).
2. **Handler asset**: replace inline placeholder with the real `services/compliance/` bundle (+ `clairo_shared`).
3. **SSM read grant**: allow reading `gdpr_rules_ref` parameter.

No infra questions required — resources already decided in U0 (see `shared-infrastructure.md`).

## Component → Infrastructure Mapping
| U4 Component | Infrastructure (U0) | Access |
|---|---|---|
| Compliance Handler (Lambda) | `clairo-dev-compliance` (1024/5min) | executes |
| GDPR Validator | Bedrock Claude Sonnet | InvokeModel |
| Rules loading | SSM `gdpr_rules_ref` + S3 (rules doc) | SSM read, S3 read |
| Explanation Generator | S3 `documents` (explanations/ prefix) | write |
| Persist findings | DynamoDB `clairo-dev-claims` | read/write |
| Audit | DynamoDB `clairo-dev-audit` | PutItem only |

## IAM (U0 agents stack, compliance role) — additions in U4 code-gen
- Existing: Bedrock invoke, S3 documents RW, DynamoDB claims RW, Audit PutItem.
- **Add**: `ssm:GetParameter` for the gdpr_rules_ref parameter (and S3 read on kb-source if the rules doc lives there).

## Changes to Apply in Code Generation
- `agents_stack.py`: compliance → `_make_service_function("compliance", ...)` at 1024/5min; add SSM GetParameter grant; grant kb-source read (rules doc location).
- Extend `build_lambdas.sh` SERVICES to include `compliance`.
