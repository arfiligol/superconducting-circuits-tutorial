"""Use-case style runner for Simulation post-processing pipelines."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from app.services.post_processing_step_registry import run_post_processing_step
from core.simulation.application.post_processing import (
    PortMatrixSweep,
    PortMatrixSweepPoint,
    PortMatrixSweepRun,
    build_port_y_sweep,
)
from core.simulation.application.run_simulation import simulation_sweep_run_from_payload
from core.simulation.domain.circuit import CircuitDefinition, SimulationResult


@dataclass(frozen=True)
class PostProcessingRunRequest:
    """Input DTO for one post-processing pipeline execution."""

    result: SimulationResult
    sweep_payload: dict[str, Any] | None
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

    runtime_output: PortMatrixSweep | PortMatrixSweepRun
    preview_sweep: PortMatrixSweep
    flow_spec: dict[str, Any]
    normalized_steps: list[dict[str, Any]]

    @property
    def sweep(self) -> PortMatrixSweep:
        """Backward-compatible UI preview sweep accessor."""
        return self.preview_sweep


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
    def _execute_single_result(result: SimulationResult) -> tuple[
        PortMatrixSweep, list[dict[str, Any]], list[dict[str, Any]]
    ]:
        sweep = build_port_y_sweep(
            result=result,
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
        return (sweep, flow_steps, normalized_steps)

    run_kind = "single_result"
    sweep_axes: list[dict[str, Any]] = []
    point_count = 1
    preview_projection: dict[str, Any] | None = None
    runtime_output: PortMatrixSweep | PortMatrixSweepRun

    if (
        isinstance(request.sweep_payload, dict)
        and str(request.sweep_payload.get("run_kind", "")).strip() == "parameter_sweep"
    ):
        input_sweep_run = simulation_sweep_run_from_payload(request.sweep_payload)
        if not input_sweep_run.points:
            raise ValueError("Parameter sweep payload has no points for post-processing.")
        point_outputs: list[PortMatrixSweepPoint] = []
        flow_steps: list[dict[str, Any]] | None = None
        normalized_steps: list[dict[str, Any]] | None = None
        for point in input_sweep_run.points:
            point_sweep, point_flow_steps, point_normalized_steps = _execute_single_result(
                point.result
            )
            if flow_steps is None:
                flow_steps = point_flow_steps
            if normalized_steps is None:
                normalized_steps = point_normalized_steps
            point_outputs.append(
                PortMatrixSweepPoint(
                    point_index=int(point.point_index),
                    axis_indices=tuple(int(index) for index in point.axis_indices),
                    axis_values={
                        str(target_value_ref): float(value)
                        for target_value_ref, value in point.axis_values.items()
                    },
                    sweep=point_sweep,
                )
            )

        runtime_output = PortMatrixSweepRun(
            axes=tuple(input_sweep_run.axes),
            points=tuple(point_outputs),
            representative_point_index=int(input_sweep_run.representative_point_index),
        )
        preview_sweep = runtime_output.representative_sweep
        representative_point = input_sweep_run.points[input_sweep_run.representative_point_index]
        run_kind = "parameter_sweep"
        sweep_axes = [
            {
                "target_value_ref": str(axis.target_value_ref),
                "unit": str(axis.unit),
                "values": [float(value) for value in axis.values],
            }
            for axis in input_sweep_run.axes
        ]
        point_count = runtime_output.point_count
        preview_projection = {
            "kind": "representative_point",
            "point_index": int(representative_point.point_index),
            "axis_indices": [int(index) for index in representative_point.axis_indices],
            "axis_values": {
                str(target_value_ref): float(value)
                for target_value_ref, value in representative_point.axis_values.items()
            },
        }
        resolved_flow_steps = flow_steps or []
        resolved_normalized_steps = normalized_steps or []
    else:
        preview_sweep, resolved_flow_steps, resolved_normalized_steps = _execute_single_result(
            request.result
        )
        runtime_output = preview_sweep

    has_enabled_coordinate_transform = any(
        bool(step.get("enabled", True))
        and str(step.get("type", "coordinate_transform")) == "coordinate_transform"
        for step in resolved_normalized_steps
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
        "steps": resolved_flow_steps,
        "run_kind": run_kind,
        "point_count": point_count,
        "sweep_axes": sweep_axes,
        "preview_projection": preview_projection,
        "hfss_comparable": hfss_comparable,
        "hfss_not_comparable_reason": hfss_not_comparable_reason,
    }
    return PostProcessingRunResult(
        runtime_output=runtime_output,
        preview_sweep=preview_sweep,
        flow_spec=flow_spec,
        normalized_steps=resolved_normalized_steps,
    )


__all__ = [
    "PostProcessingRunRequest",
    "PostProcessingRunResult",
    "execute_post_processing_pipeline",
]
