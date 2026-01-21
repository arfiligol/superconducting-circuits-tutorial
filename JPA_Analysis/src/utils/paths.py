from __future__ import annotations

from pathlib import Path


def _project_root() -> Path:
    """Return the repository root (two levels above this file)."""
    return Path(__file__).resolve().parents[2]


def _ensure_directory(path: Path) -> None:
    """Create the directory if it does not already exist."""
    path.mkdir(parents=True, exist_ok=True)


PROJECT_ROOT: Path = _project_root()
DATA_DIR: Path = PROJECT_ROOT / "data"

RAW_DATA_DIR: Path = DATA_DIR / "raw"
RAW_MEASUREMENT_DIR: Path = RAW_DATA_DIR / "measurement"
RAW_CIRCUIT_SIMULATION_DIR: Path = RAW_DATA_DIR / "circuit_simulation"
RAW_LAYOUT_SIMULATION_DIR: Path = RAW_DATA_DIR / "layout_simulation"

RAW_LAYOUT_ADMITTANCE_DIR: Path = RAW_LAYOUT_SIMULATION_DIR / "admittance"
RAW_LAYOUT_PHASE_DIR: Path = RAW_LAYOUT_SIMULATION_DIR / "phase"
RAW_MEASUREMENT_FLUX_DEPENDENCE_DIR: Path = RAW_MEASUREMENT_DIR / "flux_dependence"

PREPROCESSED_DATA_DIR: Path = DATA_DIR / "preprocessed"
PROCESSED_DATA_DIR: Path = DATA_DIR / "processed"
PROCESSED_REPORTS_DIR: Path = PROCESSED_DATA_DIR / "reports"

# Ensure the canonical directory tree exists so scripts can write outputs safely.
for directory in (
    RAW_MEASUREMENT_DIR,
    RAW_CIRCUIT_SIMULATION_DIR,
    RAW_LAYOUT_SIMULATION_DIR,
    RAW_LAYOUT_ADMITTANCE_DIR,
    RAW_LAYOUT_PHASE_DIR,
    RAW_MEASUREMENT_FLUX_DEPENDENCE_DIR,
    PREPROCESSED_DATA_DIR,
    PROCESSED_REPORTS_DIR,
):
    _ensure_directory(directory)
