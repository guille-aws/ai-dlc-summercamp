# CLAIRO — First Deployment Runbook (dev, synthetic data)

> ⚠️ **This provisions real, billable AWS resources** (Lambda, DynamoDB, S3, API Gateway, Cognito, OpenSearch Serverless, Bedrock, Amplify). It also **requires Amazon Bedrock model access** to be enabled in your account. Use **synthetic data only** (Security/Resiliency baselines are off).

## 0. Prerequisites (one-time)

### 0.1 Install the AWS CLI (currently missing on this machine)
```bash
# macOS (Homebrew)
brew install awscli
# verify
aws --version
```

### 0.2 Verify credentials + region
```bash
aws sts get-caller-identity      # confirms creds work
aws configure get region         # should print us-east-1
```

### 0.3 Enable Bedrock model access
In the AWS Console → Amazon Bedrock → Model access, enable:
- **Anthropic Claude 3.5 Sonnet** (`anthropic.claude-3-5-sonnet-20240620-v1:0`)
- A **Titan/Embeddings** model if you use it for the Knowledge Base.

### 0.4 Node/Python toolchain
- Node 20+ (Next.js prefers 22/24), npm 10+
- Python 3.12+, and the infra venv already created at `infra/.venv`

## 1. Build & synthesize (safe, no resources)
```bash
cd /Users/ggarcava/Desktop/Kiro/AI-DLC
bash scripts/build_lambdas.sh          # vendor clairo_shared into services
cd infra
.venv/bin/pip install -r requirements.txt   # if not already
npx cdk synth                          # expect 9 stacks
```

## 2. Bootstrap CDK (once per account/region)
```bash
cd infra
npx cdk bootstrap aws://<ACCOUNT_ID>/us-east-1
```

## 3. Deploy the backend
```bash
cd infra
npx cdk deploy --all --require-approval never
```
Capture these outputs (from the console or `cdk deploy` logs):
- API Gateway base URL (Clairo-dev-Api)
- Cognito User Pool Id + Web Client Id (Clairo-dev-Auth)
- S3 bucket names: `clairo-dev-documents`, `clairo-dev-kb-source`
- OpenSearch Serverless collection ARN / Bedrock KB (Clairo-dev-Kb)

## 4. Seed data (see scripts/seed_data.sh helper)
```bash
bash scripts/seed_data.sh
```
This uploads a sample GDPR policy doc and a sample policy document to `clairo-dev-kb-source`, and sets the SSM `gdpr_rules_ref`. (Review/edit the sample docs first.)

### 4.1 Create the Bedrock Knowledge Base + data source (manual/console for MVP)
- In Bedrock → Knowledge Bases, create a KB backed by the `clairo-dev-*` OpenSearch Serverless collection, data source = `s3://clairo-dev-kb-source/`.
- Note the **Knowledge Base Id** and **Data Source Id**.
- Redeploy agents with these set so Lambdas pick them up:
```bash
export CLAIRO_KB_ID=<kb-id>
export CLAIRO_KB_DATA_SOURCE_ID=<data-source-id>
cd infra && npx cdk deploy Clairo-dev-Agents Clairo-dev-Api --require-approval never
```

## 5. Create Cognito users
```bash
# Example (replace pool id):
aws cognito-idp admin-create-user --user-pool-id <POOL_ID> --username reviewer@example.com
aws cognito-idp admin-add-user-to-group --user-pool-id <POOL_ID> --username reviewer@example.com --group-name Reviewer
# Set a permanent password:
aws cognito-idp admin-set-user-password --user-pool-id <POOL_ID> --username reviewer@example.com --password '<StrongPass1!>' --permanent
```
Configure the app client hosted-UI domain + callback URLs if using Amplify hosted sign-in.

## 6. Deploy the web UI
```bash
cd web
# set the env from stack outputs:
export NEXT_PUBLIC_CLAIRO_API_URL=<api-url>
export NEXT_PUBLIC_CLAIRO_USER_POOL_ID=<pool-id>
export NEXT_PUBLIC_CLAIRO_USER_POOL_CLIENT_ID=<client-id>
export NEXT_PUBLIC_CLAIRO_REGION=us-east-1
npm install
npm run build            # static export -> web/out
```
Connect the Amplify app (Clairo-dev-Web) to your repo/branch, or upload `web/out` as a manual deployment. Set the same NEXT_PUBLIC_* values as Amplify environment variables.

## 7. Smoke test (see integration-test-instructions.md)
- `POST /claims` with a synthetic claim → poll `GET /claims/{id}` to Decided.
- Force a low-confidence claim → appears in `GET /reviews` → review in UI.
- Override → confirm `corrective/{id}.md` in kb-source + audit entry.

## 8. Tear down (stop costs)
```bash
cd infra && npx cdk destroy --all
```

## Known follow-ups before real (non-synthetic) use
- Bump Next.js off the flagged advisory version.
- Enable Security + Resiliency baselines; only then process real PHI.
- Add automated test suites; consider a formal WCAG audit.
