"""Use-case style runner for Simulation post-processing pipelines."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from app.services.post_processing_step_registry import run_post_processing_step
from core.simulation.application.post_processing import PortMatrixSweep, build_port_y_sweep
from core.simulation.domain.circuit import CircuitDefinition, SimulationResult


@dataclass(frozen=True)
class PostProcessingRunRequest:
    """Input DTO for one post-processing pipeline execution."""

    result: SimulationResult
    input_source: str
    mode_filter: str
    mode_token: str
    reference_impedance_ohm: float
    step_sequence: list[dict[str, Any]]
    circuit_definition: CircuitDefinition | None
    has_ptc_result: bool


@dataclass(frozen=True)
class PostProcessingRunResult:
    """Output DTO for one post-processing pipeline execution."""

    sweep: PortMatrixSweep
    flow_spec: dict[str, Any]
    normalized_steps: list[dict[str, Any]]


def execute_post_processing_pipeline(
    request: PostProcessingRunRequest,
    *,
    estimate_auto_weights: Callable[[CircuitDefinition, int, int], tuple[float, float] | None],
) -> PostProcessingRunResult:
    """Execute all enabled post-processing steps and build one flow-spec snapshot."""
    mode_token = str(request.mode_token or "").strip()
    if not mode_token:
        raise ValueError("Please select one mode before running post-processing.")
    reference_impedance_ohm = float(request.reference_impedance_ohm)
    if reference_impedance_ohm <= 0:
        raise ValueError("Z0 must be positive.")

    mode = SimulationResult.parse_mode_token(mode_token)
    sweep = build_port_y_sweep(
        result=request.result,
        mode=mode,
        reference_impedance_ohm=reference_impedance_ohm,
    )
    flow_steps: list[dict[str, Any]] = []
    normalized_steps: list[dict[str, Any]] = []

    for step in request.step_sequence:
        step_payload = dict(step)
        if not bool(step_payload.get("enabled", True)):
            normalized_steps.append(step_payload)
            continue
        execution = run_post_processing_step(
            sweep=sweep,
            step=step_payload,
            circuit_definition=request.circuit_definition,
            estimate_auto_weights=estimate_auto_weights,
        )
        sweep = execution.sweep
        flow_steps.append(execution.flow_step)
        normalized_steps.append(execution.normalized_step)

    has_enabled_coordinate_transform = any(
        bool(step.get("enabled", True))
        and str(step.get("type", "coordinate_transform")) == "coordinate_transform"
        for step in normalized_steps
    )
    hfss_not_comparable_reasons: list[str] = []
    if not request.has_ptc_result:
        hfss_not_comparable_reasons.append("Port Termination Compensation is disabled.")
    if request.input_source != "ptc_y":
        hfss_not_comparable_reasons.append("Input Y Source is not PTC Y.")
    if not has_enabled_coordinate_transform:
        hfss_not_comparable_reasons.append("Coordinate Transformation step is missing.")
    hfss_comparable = not hfss_not_comparable_reasons
    hfss_not_comparable_reason = (
        "; ".join(hfss_not_comparable_reasons) if hfss_not_comparable_reasons else ""
    )

    flow_spec: dict[str, Any] = {
        "input_y_source": request.input_source,
        "mode_filter": request.mode_filter,
        "mode_token": SimulationResult.mode_token(mode),
        "reference_impedance_ohm": reference_impedance_ohm,
        "steps": flow_steps,
        "hfss_comparable": hfss_comparable,
        "hfss_not_comparable_reason": hfss_not_comparable_reason,
    }
    return PostProcessingRunResult(
        sweep=sweep,
        flow_spec=flow_spec,
        normalized_steps=normalized_steps,
    )


__all__ = [
    "PostProcessingRunRequest",
    "PostProcessingRunResult",
    "execute_post_processing_pipeline",
]
