#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

mkdir -p "$ROOT_DIR/.cache/npm/frontend" "$ROOT_DIR/.cache/npm/desktop"

echo "[rewrite-install] frontend"
npm install --prefix "$ROOT_DIR/frontend" --cache "$ROOT_DIR/.cache/npm/frontend"

echo "[rewrite-install] backend"
(
  cd "$ROOT_DIR/backend"
  uv sync
)

echo "[rewrite-install] desktop"
npm install --prefix "$ROOT_DIR/desktop" --cache "$ROOT_DIR/.cache/npm/desktop"

echo "[rewrite-install] complete"
