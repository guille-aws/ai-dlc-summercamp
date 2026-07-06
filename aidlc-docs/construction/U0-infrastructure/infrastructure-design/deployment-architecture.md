# CLAIRO U0 - Deployment Architecture

## Deployment Diagram (text)
```
                         +---------------------------+
                         |   AWS Amplify Hosting     |  (U7 Reviewer Web UI)
                         +-------------+-------------+
                                       | HTTPS (Cognito JWT)
                                       v
+------------------+          +--------+---------+
| Submitter /      |  HTTPS   |  API Gateway     |  (role-scoped REST)
| Upstream System  +--------->+  (Claim API)     |
+------------------+          +--------+---------+
                                       | invoke
                                       v
                              +--------+---------+        +------------------+
                              | Orchestrator     |------->| Bedrock AgentCore|
                              | Lambda (U5)      |        +------------------+
                              +--+----+----+-----+
                                 |    |    |
             +-------------------+    |    +--------------------+
             v                        v                         v
     +---------------+       +----------------+        +----------------+
     | Intake Lambda |       | Adjudication   |        | Compliance     |
     | (U2)          |       | Lambda (U3)    |        | Lambda (U4)    |
     +----+-----+----+       +--------+-------+        +--------+-------+
          |     |                     | read                    |
    Textract  Bedrock                 v                         v
          |                    +--------------+          +-----------+
          v                    | Bedrock KB / |          | S3        |
     +---------+               | OpenSearch   |          | explanations
     | S3      |               | Serverless   |          +-----------+
     | documents|              +------+-------+
     +---------+                      ^ write
                                      |
                              +-------+--------+
                              | Feedback Lambda|  (U6, EventBridge-triggered on override)
                              +----------------+

  Data plane: DynamoDB Claims table, DynamoDB Audit table (append-only), SSM Parameter Store
  Eventing:   S3 upload --> EventBridge --> Orchestrator; Override --> EventBridge --> Feedback
  Observability: CloudWatch Logs + Alarms per Lambda
```

## Request Flows
1. **API submission**: Submitter → API Gateway → Orchestrator Lambda → pipeline.
2. **Event submission**: S3 upload → S3 notification → EventBridge → Orchestrator Lambda.
3. **Pipeline**: Orchestrator → Intake → Adjudication (KB read) → Compliance → Routing.
4. **Auto path**: confidence ≥ threshold → finalize (DynamoDB status `Decided`).
5. **Human path**: confidence < threshold → create review task → pause (`Pending Review`). Reviewer UI (Amplify) → API Gateway → Review Lambda → resume Orchestrator.
6. **Feedback**: override → EventBridge → Feedback Lambda → KB write.

## Deployment Process
- `cdk bootstrap` (once per account/region).
- `cdk deploy --all` provisions stacks in dependency order (data/auth/kb → agents/api/events/config/observability → web).
- Lambda code packaged from `services/*` and `libs/clairo_shared`; web from `web/` to Amplify.

## Environment
- Single `dev` environment; region configurable via CDK context/env vars.
