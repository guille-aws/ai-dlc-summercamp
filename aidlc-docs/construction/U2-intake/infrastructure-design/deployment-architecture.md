# CLAIRO U2 Intake - Deployment Architecture

## Deployment Model
U2 deploys as the `clairo-dev-intake` Lambda (defined in U0's agents stack), packaged with `services/intake/` + `clairo_shared`.

## Diagram (text)
```
[API submission] --> Orchestrator (U5) --\
                                          >--> Intake Lambda (clairo-dev-intake, 1024MB/5min)
[S3 upload] --> EventBridge --> Orchestrator/
                                          |
             +----------------------------+----------------------------+
             v                v               v              v          v
        Textract          Bedrock         S3 documents   DynamoDB     DynamoDB
        (OCR)          (Claude Sonnet)     (read docs)    Claims       Audit
```

## Packaging
- Lambda asset = `services/intake/` bundled with the `clairo_shared` library.
- Dependencies (boto3 provided by Lambda runtime; `clairo_shared` bundled).

## Deploy
- Part of `cdk deploy Clairo-dev-Agents` (and dependent stacks). Intake sizing/handler updated in the agents stack.

## First Testable Slice (note)
- A meaningful end-to-end test requires U2 + U3 + U4 + U5 real handlers. After those, deploy via `cdk deploy --all` and submit a synthetic claim to exercise the pipeline. U2 alone can be smoke-tested by invoking the intake Lambda with a sample event once its handler is generated.
