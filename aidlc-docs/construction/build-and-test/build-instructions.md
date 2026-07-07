# Build Instructions

## Prerequisites
- **Python**: 3.12+ (CDK app + Lambda services)
- **Node.js**: 20+ (web UI; note: 22/24 recommended per Next.js), npm 10+
- **AWS CDK CLI**: `npm i -g aws-cdk` (or use `npx cdk`)
- **AWS credentials**: configured for the target account/region
- **Environment**: single `dev` environment; region via CDK context/env

## Build Steps

### 1. Vendor the shared library into services
```bash
bash scripts/build_lambdas.sh
```
This copies `libs/clairo_shared/clairo_shared` into each `services/*` directory so it is bundled into the Lambda deployment packages. **Required before every `cdk synth`/`cdk deploy`.**

### 2. Set up the infra Python environment
```bash
cd infra
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

### 3. Synthesize / build the infrastructure
```bash
# from infra/
npx cdk synth        # validate synthesis of all 9 stacks
```
Expected: CloudFormation templates for
`Clairo-dev-{Data,Auth,Kb,Config,Agents,Api,Events,Observability,Web}`.

### 4. Build the web UI
```bash
cd web
npm install
npm run build        # typecheck + static export to web/out
```
Expected: static export of routes `/`, `/review`, `/status`, `/404`.

### 5. Deploy (optional, to a real AWS account)
```bash
cd infra
npx cdk bootstrap    # once per account/region
npx cdk deploy --all
```

## Build Artifacts
- CDK cloud assembly: `infra/cdk.out/` (gitignored)
- Web static export: `web/out/` (gitignored)
- Lambda assets: bundled per service (with vendored `clairo_shared`)

## Troubleshooting
### Synth fails: `ModuleNotFoundError: clairo_shared`
- **Cause**: services not vendored. **Fix**: run `bash scripts/build_lambdas.sh`.
### Synth fails: amplify-alpha import error
- **Cause**: `aws-cdk.aws-amplify-alpha` version mismatch. **Fix**: ensure it matches `aws-cdk-lib` version in `infra/requirements.txt`.
### Web build: Next.js security advisory
- **Note**: `next@14.2.5` flagged an advisory; bump to a patched version before real deployment.
