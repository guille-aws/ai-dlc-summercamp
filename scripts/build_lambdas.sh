#!/usr/bin/env bash
# Vendor the shared library into each service directory so it is bundled into
# the Lambda deployment package. Run before `cdk deploy`.
#
# Usage: bash scripts/build_lambdas.sh
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SHARED_SRC="$REPO_ROOT/libs/clairo_shared/clairo_shared"

SERVICES=("intake" "adjudication")

for svc in "${SERVICES[@]}"; do
  SVC_DIR="$REPO_ROOT/services/$svc"
  if [ ! -d "$SVC_DIR" ]; then
    echo "skip: $SVC_DIR not found"
    continue
  fi
  echo "Vendoring clairo_shared into services/$svc ..."
  rm -rf "$SVC_DIR/clairo_shared"
  cp -R "$SHARED_SRC" "$SVC_DIR/clairo_shared"
done

echo "Done. Service directories now contain a vendored clairo_shared copy."
