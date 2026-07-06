# CLAIRO - Shared Infrastructure Reference

This is the shared infrastructure provisioned by U0 and consumed by all other units. Per-unit infrastructure design docs reference this file rather than redefining shared resources.

## Shared AWS Resources

| Resource | Name (logical) | Purpose | Consumers |
|---|---|---|---|
| DynamoDB table | `Claims` | Single claim record + status + per-stage results | U1 (repo), U2–U5 |
| DynamoDB table | `Audit` (append-only) | Immutable audit trail | U1 (audit logger), all |
| S3 bucket | `documents` | Raw claim docs + `explanations/` prefix | U2, U4 |
| S3 bucket | `kb-source` | Knowledge base source documents | KB, U6 |
| Bedrock Knowledge Base | `policy-kb` | Policy retrieval (OpenSearch Serverless) | U3 (read), U6 (write) |
| Cognito user pool | `clairo-users` | UI auth; groups: Submitter, Reviewer, Supervisor | U5, U7 |
| API Gateway | `clairo-api` | Role-scoped REST endpoints | U5, U7 |
| EventBridge bus | default/custom | Internal events (upload, override) | U2, U5, U6 |
| SSM Parameter Store | `/clairo/*` | `confidence_threshold`, `gdpr_rules_ref` | U1 config provider, U4, U5 |
| CloudWatch | log groups + alarms | Logs, error/throttle alarms | all Lambdas |
| Amplify Hosting | `clairo-web` | Reviewer UI hosting | U7 |

## Shared Conventions
- **Region**: single, configurable via CDK env.
- **Naming**: `clairo-{env}-{resource}`.
- **IAM**: per-Lambda least-privilege roles; KB read/write split (U3 read, U6 write); Audit table write-only (PutItem) to enforce append-only.
- **Encryption**: AWS-managed keys at rest (DynamoDB, S3).
- **Config access**: units read runtime config from Parameter Store via the shared Config Provider (U1).

## SSM Parameters (initial)
| Parameter | Example value | Used by |
|---|---|---|
| `/clairo/dev/confidence_threshold` | `0.80` | Routing Evaluator (U5) |
| `/clairo/dev/gdpr_rules_ref` | `s3://clairo-dev-kb-source/gdpr-rules.json` | Compliance (U4) |
