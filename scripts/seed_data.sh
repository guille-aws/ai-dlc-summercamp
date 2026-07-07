#!/usr/bin/env bash
# Seed sample knowledge-base + GDPR data for a CLAIRO dev deployment.
# Requires: AWS CLI configured, stacks already deployed.
# Uses SYNTHETIC data only.
set -euo pipefail

ENV_NAME="${CLAIRO_ENV:-dev}"
REGION="${AWS_REGION:-us-east-1}"
KB_SOURCE_BUCKET="clairo-${ENV_NAME}-kb-source"
GDPR_PARAM="/clairo/${ENV_NAME}/gdpr_rules_ref"

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SEED_DIR="$REPO_ROOT/seed"

if ! command -v aws >/dev/null 2>&1; then
  echo "ERROR: AWS CLI not found. Install it first (see DEPLOYMENT-RUNBOOK.md)." >&2
  exit 1
fi

echo "Uploading sample policy document to s3://${KB_SOURCE_BUCKET}/policies/ ..."
aws s3 cp "$SEED_DIR/sample-health-policy.md" "s3://${KB_SOURCE_BUCKET}/policies/sample-health-policy.md" --region "$REGION"

echo "Uploading sample GDPR rules to s3://${KB_SOURCE_BUCKET}/gdpr-rules.md ..."
aws s3 cp "$SEED_DIR/sample-gdpr-rules.md" "s3://${KB_SOURCE_BUCKET}/gdpr-rules.md" --region "$REGION"

echo "Setting SSM parameter ${GDPR_PARAM} ..."
aws ssm put-parameter \
  --name "$GDPR_PARAM" \
  --value "s3://${KB_SOURCE_BUCKET}/gdpr-rules.md" \
  --type String --overwrite --region "$REGION"

echo "Done. Next: create/sync the Bedrock Knowledge Base data source over s3://${KB_SOURCE_BUCKET}/ (see DEPLOYMENT-RUNBOOK.md step 4.1)."
