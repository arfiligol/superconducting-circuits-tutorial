#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

SITE_ROOT="docs/site"
SITE_PREFIX="$(uv run python - <<'PY'
from urllib.parse import urlparse
import tomllib
from pathlib import Path

data = tomllib.loads(Path("zensical.toml").read_text(encoding="utf-8"))
site_url = str(data.get("project", {}).get("site_url", ""))
print(urlparse(site_url).path.strip("/"))
PY
)"

uv run python scripts/check_docs_nav_routes.py --check-source

bash ./scripts/prepare_docs_locales.sh

uv run --group dev zensical build -f zensical.toml

if [ -n "${SITE_PREFIX}" ]; then
  mkdir -p "${SITE_ROOT}/${SITE_PREFIX}"
  rsync -a --delete \
    --exclude "${SITE_PREFIX}/" \
    "${SITE_ROOT}/" "${SITE_ROOT}/${SITE_PREFIX}/"
fi

uv run python scripts/check_docs_nav_routes.py --check-built
