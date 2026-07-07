# CLAIRO U4 Compliance - Deployment Architecture

## Deployment Model
U4 deploys as the `clairo-dev-compliance` Lambda (U0 agents stack), packaged with `services/compliance/` + vendored `clairo_shared`.

## Diagram (text)
```
Orchestrator (U5) --> Compliance Lambda (clairo-dev-compliance, 1024MB/5min)
                          |
         +----------------+----------------+----------------+
         v                v                v                v
   SSM gdpr_rules_ref  S3 (rules doc)   Bedrock (LLM eval)  S3 explanations (JSON+MD)
         |
         v
   DynamoDB Claims (compliance_result, status ComplianceChecked)
   DynamoDB Audit (PutItem)
```

## Packaging
- Lambda asset = `services/compliance/` bundled with `clairo_shared` (via `scripts/build_lambdas.sh`, extended to include `compliance`).

## Deploy
- Part of `cdk deploy Clairo-dev-Agents`.

## Seed Data Prerequisite
- A GDPR policy document must exist at the S3 location referenced by `gdpr_rules_ref` (seed step for Build & Test).
