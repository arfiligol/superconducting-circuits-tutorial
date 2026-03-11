#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

SITE_ROOT="docs/site"

uv run python scripts/check_docs_nav_routes.py --check-source

bash ./scripts/prepare_docs_locales.sh

uv run --group dev zensical build -c

uv run python scripts/check_docs_nav_routes.py --check-built
