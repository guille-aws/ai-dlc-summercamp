# CLAIRO U0 Infrastructure - Infrastructure Design Plan

**Purpose**: Define the concrete AWS infrastructure (via AWS CDK Python) that all CLAIRO units deploy onto. This is the shared/system-wide infrastructure unit.

**Established context** (from prior stages — no need to re-ask):
- Cloud: AWS, single region. IaC: AWS CDK (Python). Deployment: serverless (Lambda + API Gateway + events), AgentCore orchestration.
- Data: DynamoDB (claims) + S3 (documents/explanations) + append-only audit store. KB: Bedrock Knowledge Base + OpenSearch Serverless. Auth: Cognito (UI) + IAM (service-to-service).
- Extensions (security/resiliency/PBT) OFF; MVP with synthetic data; sensible low-cost defaults allowed.

---

## Part A: Infrastructure Questions

Please answer each question by filling in the letter after the `[Answer]:` tag. Choose **X) Other** and describe if none fit. Let me know when done.

### Question 1: Audit Store Implementation
The requirements call for an append-only audit store. Which implementation for the MVP?

A) DynamoDB table with append-only access pattern (writes only, no updates/deletes via IAM) — simplest, low cost

B) S3 with Object Lock (WORM) in a dedicated audit bucket — strong immutability

C) Amazon QLDB — purpose-built immutable ledger

X) Other (please describe after [Answer]: tag below)

[Answer]: 

### Question 2: Async Intake & Eventing
How should event-driven flows (S3 upload trigger, HITL pause, override feedback) be wired?

A) S3 Event Notifications + Amazon EventBridge for internal events (upload → orchestrator; override → feedback)

B) S3 Notifications + SQS queues between stages

C) EventBridge for all events plus SQS for the review-task backlog

X) Other (please describe after [Answer]: tag below)

[Answer]: 

### Question 3: Web UI Hosting
How should the TypeScript reviewer UI (U7) be hosted?

A) Amazon S3 + CloudFront (static hosting, SPA)

B) AWS Amplify Hosting

X) Other (please describe after [Answer]: tag below)

[Answer]: 

### Question 4: Environments
How many deployment environments should the CDK app support for the MVP?

A) Single environment (e.g., `dev`)

B) Two environments (`dev` and `prod`) parameterized in CDK

X) Other (please describe after [Answer]: tag below)

[Answer]: 

### Question 5: Monitoring/Observability Baseline
What observability should infra provision by default?

A) CloudWatch Logs for all Lambdas + basic CloudWatch metrics/alarms on errors and throttles

B) The above plus AWS X-Ray tracing across the pipeline

C) The above plus a CloudWatch dashboard for claim throughput and review queue depth

X) Other (please describe after [Answer]: tag below)

[Answer]: 

### Question 6: Secrets/Config Storage
Where should runtime config (confidence threshold, GDPR rules location) and any secrets live?

A) AWS Systems Manager Parameter Store (config) — simplest for MVP

B) Parameter Store for config + AWS Secrets Manager for any secrets

X) Other (please describe after [Answer]: tag below)

[Answer]: 

---

## Part B: Execution Checklist (executed after plan approval)

- [ ] Generate `aidlc-docs/construction/U0-infrastructure/infrastructure-design/infrastructure-design.md`
- [ ] Generate `aidlc-docs/construction/U0-infrastructure/infrastructure-design/deployment-architecture.md`
- [ ] Generate `aidlc-docs/construction/shared-infrastructure.md` (shared infra reference for all units)
- [ ] Map every logical component/service to concrete AWS resources + CDK stacks
- [ ] Update aidlc-state.md and audit.md
