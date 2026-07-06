# CLAIRO U0 Infrastructure - Code Summary & Deployment

## Generated Files (workspace root, not aidlc-docs)
```
infra/
├── app.py                          # CDK app entry; wires all stacks in dependency order
├── cdk.json                        # CDK config (app command, context: clairo:env=dev)
├── requirements.txt                # aws-cdk-lib, aws-amplify-alpha, constructs
└── stacks/
    ├── __init__.py
    ├── config.py                   # ClairoConfig, naming, SSM param names, model id
    ├── data_stack.py               # DynamoDB Claims + Audit; S3 documents + kb-source
    ├── auth_stack.py               # Cognito user pool + client + role groups
    ├── kb_stack.py                 # OpenSearch Serverless collection (Bedrock KB backing)
    ├── config_stack.py             # SSM params: confidence_threshold, gdpr_rules_ref
    ├── agents_stack.py             # Intake/Adjudication/Compliance/Feedback Lambdas + IAM
    ├── api_stack.py                # API Gateway REST + orchestrator/API Lambda + Cognito authz
    ├── events_stack.py             # S3->EventBridge upload rule; override->Feedback rule
    ├── observability_stack.py      # CloudWatch error/throttle alarms
    └── web_stack.py                # Amplify Hosting app for reviewer UI
```

## Verification Performed
- Created a Python venv and installed CDK dependencies.
- Ran `python app.py` (synth): **all 9 stacks synthesized successfully** to CloudFormation templates:
  Data, Auth, Kb, Config, Agents, Api, Events, Observability, Web.

## Deployment Instructions
```bash
cd infra
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt

# One-time per account/region:
npx cdk bootstrap

# Deploy all stacks (dev environment):
npx cdk deploy --all

# Deploy a single stack:
npx cdk deploy Clairo-dev-Data
```

## Notes / Extension Points
- **Placeholder handlers**: Agent and API Lambdas use inline placeholder code. These are replaced with asset-based handlers (`services/<unit>`) as each unit's code is generated (U1–U6).
- **Bedrock Knowledge Base**: The OpenSearch Serverless collection is provisioned; the Bedrock KB data-source/embedding wiring is a documented extension point for the Adjudication (U3) and Feedback (U6) integration.
- **Amplify source**: The reviewer UI repo/branch connection is configured post-deploy to keep credentials out of the CDK app.
- **Environment**: single `dev` env; region via `config.region` / CDK context.
- **Security extension OFF**: encryption at rest (AWS-managed keys) and least-privilege IAM applied as sensible defaults; no advanced hardening.
