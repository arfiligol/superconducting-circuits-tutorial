#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PID_DIR="$ROOT_DIR/tmp/rewrite_pids"

stop_service() {
  local name="$1"
  local pid_file="$PID_DIR/$name.pid"

  if [[ ! -f "$pid_file" ]]; then
    echo "[rewrite-stop] $name not running"
    return
  fi

  local pid
  pid="$(cat "$pid_file")"
  if kill -0 "$pid" 2>/dev/null; then
    kill "$pid"
    wait "$pid" 2>/dev/null || true
    echo "[rewrite-stop] stopped $name (pid=$pid)"
  else
    echo "[rewrite-stop] $name pid file was stale (pid=$pid)"
  fi
  rm -f "$pid_file"
}

stop_service frontend
stop_service backend
