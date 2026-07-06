# CLAIRO U3 Adjudication - Deployment Architecture

## Deployment Model
U3 deploys as the `clairo-dev-adjudication` Lambda (U0 agents stack), packaged with `services/adjudication/` + vendored `clairo_shared`.

## Diagram (text)
```
Orchestrator (U5) --> Adjudication Lambda (clairo-dev-adjudication, 1024MB/5min)
                          |
             +------------+-------------------+
             v                                v
   Bedrock KB (RetrieveAndGenerate)      DynamoDB Claims (persist decision)
   (top-5 policy passages + generation)  DynamoDB Audit (PutItem)
```

## Packaging
- Lambda asset = `services/adjudication/` bundled with `clairo_shared` (via `scripts/build_lambdas.sh`, extended to include `adjudication`).

## Deploy
- Part of `cdk deploy Clairo-dev-Agents`.

## Knowledge Base Prerequisite
- A Bedrock Knowledge Base must exist over the OpenSearch Serverless collection with policy docs ingested; its id is passed to the adjudication Lambda via env. KB creation/ingestion is an operational step (seed data) noted for Build & Test.
