# CLAIRO U4 Compliance - Code Generation Plan

**Unit**: U4 Compliance (serverless Lambda agent)
**Code location**: `services/compliance/`
**Depends on**: U1 (`clairo_shared`), U0 (Bedrock, S3, SSM, DynamoDB, Audit).
**Stories**: US-05.

## Design Inputs
- FD/NFR/Infra under `aidlc-docs/construction/U4-compliance/`.

## Decisions Applied
- NL GDPR policy loaded SSM→S3 per invocation; pure LLM evaluation; annotate-only; JSON+Markdown explanation; 1024/5min; result tuples; injectable clients; no unit tests.

## Generation Steps

- [x] **Step 1: Scaffolding** — `services/compliance/requirements.txt`, `__init__.py`.
- [x] **Step 2: GDPR Validator** — `gdpr_validator.py`.
- [x] **Step 3: Explanation Generator** — `explanation.py` (JSON + Markdown).
- [x] **Step 4: Handler** — `handler.py` (ComplianceService, annotate-only; decision passed via event).
- [x] **Step 5: CDK update** — compliance real asset 1024/5min; ssm:GetParameter + kb-source read; build_lambdas.sh extended.
- [x] **Step 6: Verify** — build_lambdas OK; offline logic check (compliant/flagged/explanation) passed; cdk synth passed (3 Lambdas @1024MB, ssm grant, asset bundles clairo_shared).
- [x] **Step 7: Documentation** — `aidlc-docs/construction/U4-compliance/code/README.md`.

## Notes
- Injectable clients for offline verification.
- No unit tests (NFR Q3:A); verify via logic check + synth here.
