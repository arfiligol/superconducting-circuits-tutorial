#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo "[smoke] ruff check"
uv run ruff check .

echo "[smoke] pytest (full)"
uv run pytest

echo "[smoke] playwright characterization e2e"
RUN_PLAYWRIGHT_CHARACTERIZATION_E2E=1 \
  uv run pytest tests/app/e2e/test_characterization_playwright.py -q

echo "[smoke] playwright josephson e2e"
RUN_PLAYWRIGHT_JOSEPHSON_E2E=1 \
  uv run pytest tests/app/e2e/test_josephson_examples_playwright.py \
    -k "linear_series_lc or port_termination_compensation_modes_in_ui" -q

echo "[smoke] complete"
