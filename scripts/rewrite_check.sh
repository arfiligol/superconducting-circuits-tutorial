#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "[rewrite-check] frontend lint"
npm run lint --prefix "$ROOT_DIR/frontend"

echo "[rewrite-check] frontend typecheck"
npm run typecheck --prefix "$ROOT_DIR/frontend"

echo "[rewrite-check] frontend test"
npm run test --prefix "$ROOT_DIR/frontend"

echo "[rewrite-check] backend startup smoke"
(
  cd "$ROOT_DIR/backend"
  uv run python - <<'PY'
from src.app.main import app

print(app.title)
print([route.path for route in app.router.routes])
PY
)

echo "[rewrite-check] backend pytest"
(
  cd "$ROOT_DIR/backend"
  uv run pytest
)

echo "[rewrite-check] desktop lint"
npm run lint --prefix "$ROOT_DIR/desktop"

echo "[rewrite-check] complete"
