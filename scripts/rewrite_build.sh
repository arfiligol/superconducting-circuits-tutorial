#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "[rewrite-build] frontend"
npm run build --prefix "$ROOT_DIR/frontend"

echo "[rewrite-build] desktop"
npm run build --prefix "$ROOT_DIR/desktop"

echo "[rewrite-build] complete"
