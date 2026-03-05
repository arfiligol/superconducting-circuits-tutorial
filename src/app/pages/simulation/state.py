"""State factory helpers for Simulation page."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from typing import Any


def default_result_view_state(
    *,
    family: str = "s",
    metric: str = "magnitude_linear",
    z0: float = 50.0,
    family_sources: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    """Build one canonical result-view state payload."""
    state: dict[str, Any] = {
        "family": family,
        "metric": metric,
        "z0": z0,
        "traces": [],
    }
    if family_sources:
        state["family_sources"] = dict(family_sources)
    return state


def default_post_processing_input_state() -> dict[str, str]:
    """Build one canonical post-processing input selector state."""
    return {"input_y_source": "raw_y"}


@dataclass
class SimulationRuntimeState:
    """Single mutable state source for Simulation page runtime."""

    status_history: list[dict[str, str]] = field(default_factory=list)
    latest_sweep: Any | None = None
    latest_flow_spec: dict[str, Any] | None = None
    latest_circuit_record: Any | None = None
    latest_source_simulation_bundle_id: int | None = None
    latest_schema_source_hash: str | None = None
    latest_simulation_setup_hash: str | None = None
    latest_simulation_result: Any | None = None
    latest_raw_save_callback: Callable[[], None] | None = None
    termination_last_warning: str = ""
    termination_last_summary: str = ""

    def append_status(self, level: str, message: str, *, time_label: str, limit: int = 30) -> None:
        """Append one simulation log row with bounded history."""
        self.status_history.append(
            {
                "level": level,
                "message": message,
                "time": time_label,
            }
        )
        if len(self.status_history) > limit:
            self.status_history.pop(0)
