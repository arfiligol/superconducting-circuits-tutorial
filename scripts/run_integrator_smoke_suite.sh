#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

run_app_startup_smoke() {
  local port="${SC_APP_PORT:-8099}"
  echo "[smoke] sc-app startup"
  SC_APP_HOST="${SC_APP_HOST:-127.0.0.1}" \
  SC_APP_PORT="$port" \
  NICEGUI_SCREEN_TEST_PORT="$port" \
  uv run python - <<'PY'
import contextlib
import http.client
import os
import socket
import subprocess
import time
from pathlib import Path

root = Path.cwd()
port = int(os.environ["SC_APP_PORT"])
env = dict(os.environ)
proc = subprocess.Popen(
    [str(root / ".venv/bin/sc-app")],
    cwd=root,
    env=env,
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL,
)
try:
    deadline = time.monotonic() + 60.0
    while time.monotonic() < deadline:
        try:
            conn = http.client.HTTPConnection("127.0.0.1", port, timeout=1)
            conn.request("GET", "/login")
            response = conn.getresponse()
            response.read()
            conn.close()
            if response.status == 200:
                print(f"sc-app ready on http://127.0.0.1:{port}")
                raise SystemExit(0)
        except Exception:
            time.sleep(0.2)
    raise SystemExit("sc-app startup smoke timed out")
finally:
    proc.terminate()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait(timeout=5)
PY
}

echo "[smoke] ruff format"
uv run ruff format . --check

echo "[smoke] ruff check"
uv run ruff check .

echo "[smoke] basedpyright"
uv run basedpyright

echo "[smoke] pytest tests/core tests/app tests/scripts"
uv run pytest tests/core tests/app tests/scripts

echo "[smoke] sc-worker-simulation startup"
uv run sc-worker-simulation --max-tasks 0

echo "[smoke] sc-worker-characterization startup"
uv run sc-worker-characterization --max-tasks 0

run_app_startup_smoke

if [[ "${SC_SMOKE_INCLUDE_EXTENDED:-0}" == "1" ]]; then
  echo "[smoke] extended playwright characterization e2e"
  RUN_PLAYWRIGHT_CHARACTERIZATION_E2E=1 \
    uv run pytest tests/app/e2e/test_characterization_playwright.py -q

  echo "[smoke] extended playwright josephson e2e"
  RUN_PLAYWRIGHT_JOSEPHSON_E2E=1 \
    uv run pytest tests/app/e2e/test_josephson_examples_playwright.py \
      -k "linear_series_lc or port_termination_compensation_modes_in_ui" -q
fi

echo "[smoke] complete"
