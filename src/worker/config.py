"""Worker-lane configuration helpers."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Final, Literal

from huey import SqliteHuey

LaneName = Literal["simulation", "characterization"]

_REPO_ROOT = Path(__file__).resolve().parents[2]
_BROKER_ENV_VARS: Final[dict[LaneName, str]] = {
    "simulation": "SC_SIMULATION_HUEY_DB_PATH",
    "characterization": "SC_CHARACTERIZATION_HUEY_DB_PATH",
}
_BROKER_DEFAULTS: Final[dict[LaneName, str]] = {
    "simulation": "simulation_huey.db",
    "characterization": "characterization_huey.db",
}


def default_stale_timeout_seconds() -> int:
    """Return the reconcile timeout used by worker smoke and startup helpers."""
    raw_value = os.getenv("SC_WORKER_STALE_TIMEOUT_SECONDS", "300")
    return max(1, int(raw_value))


def resolve_huey_broker_path(lane: LaneName) -> Path:
    """Resolve one lane-specific Huey SQLite broker path."""
    override = os.getenv(_BROKER_ENV_VARS[lane])
    if override is not None and override.strip():
        return Path(override).expanduser()
    return _REPO_ROOT / "data" / "huey" / _BROKER_DEFAULTS[lane]


def create_huey(lane: LaneName) -> SqliteHuey:
    """Create one lane-specific SQLite-backed Huey instance."""
    broker_path = resolve_huey_broker_path(lane)
    broker_path.parent.mkdir(parents=True, exist_ok=True)
    return SqliteHuey(filename=str(broker_path))
