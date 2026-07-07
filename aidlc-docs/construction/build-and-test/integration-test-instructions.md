# Integration Test Instructions

## Purpose
Validate the end-to-end claim pipeline across units on a deployed `dev` environment.

## Prerequisites (seed data / operational setup)
1. `bash scripts/build_lambdas.sh` then `cd infra && npx cdk deploy --all`.
2. **Knowledge Base**: create a Bedrock Knowledge Base over the OpenSearch Serverless collection; ingest sample health-policy documents into the `kb-source` bucket. Set `CLAIRO_KB_ID` and `CLAIRO_KB_DATA_SOURCE_ID` env for the agents/feedback Lambdas.
3. **GDPR rules**: upload a GDPR policy document to the S3 location referenced by the `/clairo/dev/gdpr_rules_ref` SSM parameter.
4. **Cognito users**: create test users in the `clairo-dev-users` pool and assign groups (Submitter, Reviewer, Supervisor). Configure the app client hosted-UI domain + callback URLs for the web app.
5. Use **synthetic data only** (no real PHI).

## Scenario 1: Auto-adjudicated claim (high confidence)
- **Steps**: `POST /claims` with a synthetic claim whose facts clearly match policy.
- **Expected**: claim advances Received → IntakeComplete → Adjudicated → ComplianceChecked → Decided; audit trail shows each step (`GET /claims/{id}/audit` as Supervisor).

## Scenario 2: Low-confidence claim → human review (US-06/07)
- **Steps**: submit a claim with ambiguous/weak policy basis so confidence < threshold.
- **Expected**: claim reaches `PendingReview`; appears in `GET /reviews`; reviewer opens it in the web UI (recommendation + confidence + highlighted evidence), submits a decision → status `Decided`.

## Scenario 3: Override → feedback loop (US-08)
- **Steps**: as Reviewer, override the recommendation with a rationale.
- **Expected**: `ClaimOverridden` event emitted; feedback Lambda writes `corrective/{claim_id}.md` to kb-source and starts a KB ingestion job; audit shows the feedback write-back.

## Scenario 4: Event-driven intake (US-02)
- **Steps**: upload a synthetic document to the `documents` bucket.
- **Expected**: S3 → EventBridge → orchestrator → intake; a claim record is created and processed.

## Scenario 5: Authorization (US-12)
- **Steps**: call `PUT /config/threshold` as a Reviewer (expect 403) and as a Supervisor (expect 200); `GET /claims/{id}/audit` as non-Supervisor (expect 403).

## Verifying Results
- **DynamoDB**: inspect the `clairo-dev-claims` and `clairo-dev-audit` tables.
- **S3**: check `documents/explanations/` and `kb-source/corrective/`.
- **CloudWatch Logs**: per-Lambda log groups for step tracing.

## Cleanup
- `npx cdk destroy --all` (dev resources use DESTROY removal policy).
