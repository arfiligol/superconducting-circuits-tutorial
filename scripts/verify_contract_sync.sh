#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "==> Running sync_api_types.sh..."
"$SCRIPT_DIR/sync_api_types.sh"

echo "==> Checking for uncommitted changes in generated schema..."
cd "$REPO_ROOT"
if git diff --exit-code frontend/src/lib/api/generated/schema.d.ts; then
  echo "✅ Contract sync verification passed. No drift detected."
else
  echo "❌ Contract drift detected! The generated schema.d.ts has changes."
  echo "Please run './scripts/sync_api_types.sh' and commit the changes."
  exit 1
fi
