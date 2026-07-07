# CLAIRO U6 Feedback - Deployment Architecture

## Diagram (text)
```
Reviewer override (U5 review) --> EventBridge (clairo.review: ClaimOverridden)
                                        |
                                        v
                          Feedback Lambda (clairo-dev-feedback)
                                        |
                     +------------------+------------------+
                     v                  v                  v
              DynamoDB Claims     S3 kb-source        Bedrock KB
              (read summary)      (corrective/{id}.md) StartIngestionJob
                                        |
                                  DynamoDB Audit (PutItem)
```

## Packaging
- Lambda asset = `services/feedback/` bundled with `clairo_shared` (via `build_lambdas.sh`, extended to include `feedback`).

## Deploy
- Part of `cdk deploy Clairo-dev-Agents` (+ Events stack already wires the trigger).

## KB Prerequisite
- Requires the Bedrock Knowledge Base + its data source id (KB_DATA_SOURCE_ID) to run ingestion; provided via env (operational config).
