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


def default_sweep_result_view_state() -> dict[str, Any]:
    """Build one canonical sweep-result view state payload."""
    return {
        "family": "s",
        "metric": "magnitude_db",
        "z0": 50.0,
        "frequency_index": 0,
        "view_axis_target_value_ref": "",
        "fixed_axis_indices": {},
        "traces": [],
        "trace_selection": {},
    }


@dataclass
class SimulationRuntimeState:
    """Single mutable state source for Simulation page runtime."""

    status_history: list[dict[str, str]] = field(default_factory=list)
    latest_sweep: Any | None = None
    latest_post_processing_runtime: Any | None = None
    latest_flow_spec: dict[str, Any] | None = None
    latest_circuit_record: Any | None = None
    latest_source_simulation_bundle_id: int | None = None
    latest_schema_source_hash: str | None = None
    latest_simulation_setup_hash: str | None = None
    latest_sweep_setup_hash: str | None = None
    latest_simulation_result: Any | None = None
    latest_simulation_sweep_payload: dict[str, Any] | None = None
    latest_raw_save_callback: Callable[[], None] | None = None
    termination_last_warning: str = ""
    termination_last_summary: str = ""
    active_log_context: dict[str, str] = field(default_factory=dict)

    def set_log_context(self, **tokens: object) -> None:
        """Replace active log context tokens for subsequent status lines."""
        self.active_log_context = {
            str(key): str(value) for key, value in tokens.items() if value not in (None, "")
        }

    def clear_log_context(self) -> None:
        """Clear active log context tokens."""
        self.active_log_context = {}

    def append_status(self, level: str, message: str, *, time_label: str, limit: int = 30) -> None:
        """Append one simulation log row with bounded history."""
        context_prefix = ""
        if self.active_log_context:
            token_text = " ".join(
                f"{key}={value}" for key, value in sorted(self.active_log_context.items())
            )
            context_prefix = f"[{token_text}] "
        self.status_history.append(
            {
                "level": level,
                "message": f"{context_prefix}{message}",
                "time": time_label,
            }
        )
        if len(self.status_history) > limit:
            self.status_history.pop(0)


@dataclass
class TerminationSetupState:
    """Mutable setup state for port-termination compensation controls."""

    enabled: bool
    mode: str
    selected_ports: list[int]
    manual_resistance_ohm_by_port: dict[int, float]

    @classmethod
    def create(cls, *, available_ports: list[int], default_ohm: float) -> TerminationSetupState:
        """Build default termination setup state."""
        return cls(
            enabled=False,
            mode="auto",
            selected_ports=list(available_ports),
            manual_resistance_ohm_by_port={
                int(port): float(default_ohm) for port in available_ports
            },
        )


@dataclass
class TerminationViewElements:
    """References for termination setup UI elements."""

    enabled_switch: Any | None = None
    mode_select: Any | None = None
    ports_select: Any | None = None
    reset_button: Any | None = None
    summary_label: Any | None = None
    details_container: Any | None = None
