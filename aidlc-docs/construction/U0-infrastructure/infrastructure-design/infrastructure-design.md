# CLAIRO U0 - Infrastructure Design

**Cloud**: AWS (single region) · **IaC**: AWS CDK (Python) · **Environment**: single `dev` (Q4:A)

## Decisions (from plan)
| # | Decision | Choice |
|---|---|---|
| Q1 | Audit store | DynamoDB table, append-only via IAM (no update/delete) |
| Q2 | Eventing | S3 Event Notifications + EventBridge for internal events |
| Q3 | Web UI hosting | AWS Amplify Hosting |
| Q4 | Environments | Single (`dev`) |
| Q5 | Observability | CloudWatch Logs + basic error/throttle alarms |
| Q6 | Config/secrets | SSM Parameter Store |

## Component → AWS Service Mapping

| Logical component/service | AWS Resource |
|---|---|
| Claim Orchestrator (U5) | Bedrock AgentCore + orchestrator Lambda |
| Intake components (U2) | Lambda(s); Amazon Textract; Bedrock (Claude Sonnet) |
| Adjudication (U3) | Lambda(s); Bedrock Knowledge Base (read) |
| Compliance (U4) | Lambda(s); Bedrock (reasoning) |
| Routing/Review/API (U5) | Lambda(s) + Amazon API Gateway (REST) |
| Feedback (U6) | Lambda (EventBridge-triggered); Bedrock KB (write) |
| Claim Repository (U1) | Amazon DynamoDB `Claims` table |
| Document Store (U1) | Amazon S3 `documents` bucket (+ `explanations` prefix) |
| Audit Logger (U1) | Amazon DynamoDB `Audit` table (append-only IAM policy) |
| Config Provider (U1) | AWS SSM Parameter Store |
| Identity & Access (U1) | Amazon Cognito user pool + IAM roles |
| Knowledge Base | Bedrock Knowledge Base + OpenSearch Serverless collection + S3 `kb-source` bucket |
| Web UI (U7) | AWS Amplify Hosting |
| Eventing | S3 Event Notifications → EventBridge; EventBridge rules → Lambda targets |
| Observability | CloudWatch Logs per Lambda; CloudWatch Alarms on Errors/Throttles |

## CDK Stack Organization
```
infra/app.py                      # CDK app entry (single dev env)
infra/stacks/
├── data_stack.py                 # DynamoDB (Claims, Audit), S3 (documents, kb-source)
├── auth_stack.py                 # Cognito user pool + groups (Submitter, Reviewer, Supervisor)
├── kb_stack.py                   # OpenSearch Serverless + Bedrock Knowledge Base
├── agents_stack.py               # Intake/Adjudication/Compliance/Feedback Lambdas + AgentCore
├── api_stack.py                  # API Gateway + orchestrator/review/API Lambdas
├── events_stack.py               # S3 notifications, EventBridge rules
├── config_stack.py               # SSM parameters (threshold, gdpr rules ref)
├── observability_stack.py        # Log groups, alarms
└── web_stack.py                  # Amplify Hosting for U7
```

## IAM / Access Control (baseline, security ext OFF but sensible defaults)
- Adjudication role: `bedrock:Retrieve` on KB (read only).
- Feedback role: KB ingestion (write only).
- Audit table: Lambda roles get `dynamodb:PutItem` only (no Update/Delete) to enforce append-only.
- Per-Lambda least-privilege roles scoped to the specific tables/buckets they use.
- Encryption at rest: AWS-managed keys on DynamoDB/S3 (low-cost default).

## Notes
- Single-region, single-environment MVP; no multi-AZ/DR design (resiliency ext OFF).
- Synthetic data only (no real PHI) per requirements NFR-4.1.
