"""
Simulation Use Cases.

This module orchestrates the simulation workflow.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from itertools import product
from typing import Any

from core.simulation.domain.circuit import (
    CircuitDefinition,
    ComponentSpec,
    ExpandedCircuitDefinition,
    FrequencyRange,
    SimulationConfig,
    SimulationResult,
)
from core.simulation.infrastructure.julia_adapter import JuliaSimulator


@dataclass(frozen=True)
class SimulationSweepTarget:
    """Sweepable `value_ref` discovered from expanded `components[*].value_ref`."""

    value_ref: str
    unit: str


@dataclass(frozen=True)
class SimulationSweepAxis:
    """One sweep axis bound to one `value_ref` target."""

    target_value_ref: str
    values: tuple[float, ...]
    unit: str

    @property
    def point_count(self) -> int:
        """Return number of grid points on this axis."""
        return len(self.values)


@dataclass(frozen=True)
class SimulationSweepPoint:
    """One concrete grid point in a sweep plan."""

    point_index: int
    axis_indices: tuple[int, ...]
    value_ref_overrides: dict[str, float]


@dataclass(frozen=True)
class SimulationSweepPlan:
    """Expanded sweep plan for one simulation run."""

    axes: tuple[SimulationSweepAxis, ...]
    points: tuple[SimulationSweepPoint, ...]

    @property
    def dimension(self) -> int:
        """Return sweep dimensionality."""
        return len(self.axes)

    @property
    def point_count(self) -> int:
        """Return total point count across all axes."""
        return len(self.points)


@dataclass(frozen=True)
class SimulationSweepPointResult:
    """One executed sweep point result."""

    point_index: int
    axis_indices: tuple[int, ...]
    axis_values: dict[str, float]
    result: SimulationResult


@dataclass(frozen=True)
class SimulationSweepRun:
    """Sweep execution output used by cache/provenance/export layers."""

    axes: tuple[SimulationSweepAxis, ...]
    points: tuple[SimulationSweepPointResult, ...]
    representative_point_index: int = 0

    @property
    def dimension(self) -> int:
        """Return sweep dimensionality."""
        return len(self.axes)

    @property
    def point_count(self) -> int:
        """Return total executed point count."""
        return len(self.points)

    @property
    def representative_result(self) -> SimulationResult:
        """Return one representative result used for quick-inspect views."""
        if not self.points:
            raise ValueError("Simulation sweep produced no points.")
        if self.representative_point_index < 0 or self.representative_point_index >= len(
            self.points
        ):
            raise ValueError("representative_point_index is out of range.")
        return self.points[self.representative_point_index].result


def run_simulation(
    circuit: CircuitDefinition,
    freq_range: FrequencyRange,
    config: SimulationConfig | None = None,
) -> SimulationResult:
    """
    Run a circuit simulation.

    This is the main entry point for simulation use cases.

    Args:
        circuit: Circuit definition.
        freq_range: Frequency sweep range.
        config: Optional simulation config. Defaults to sensible values.

    Returns:
        SimulationResult with S-parameter data.
    """
    if config is None:
        config = SimulationConfig()

    simulator = JuliaSimulator()
    return simulator.run_hbsolve(circuit, freq_range, config)


def list_simulation_sweep_targets(circuit: CircuitDefinition) -> list[SimulationSweepTarget]:
    """List unique sweepable `value_ref` targets from `components[*].value_ref`."""
    targets: dict[str, str] = {}
    parameter_specs = circuit.parameter_specs
    for component in circuit.expanded_definition.components:
        if component.value_ref is None:
            continue
        parameter = parameter_specs.get(component.value_ref)
        unit = parameter.unit if parameter is not None else component.unit
        if component.value_ref not in targets:
            targets[component.value_ref] = str(unit)
    return [
        SimulationSweepTarget(value_ref=value_ref, unit=targets[value_ref])
        for value_ref in sorted(targets)
    ]


def build_linear_sweep_values(*, start: float, stop: float, points: int) -> tuple[float, ...]:
    """Build an evenly spaced sweep axis."""
    if points < 1:
        raise ValueError("Sweep points must be >= 1.")
    if points == 1:
        return (float(start),)
    step = (float(stop) - float(start)) / float(points - 1)
    return tuple(float(float(start) + step * idx) for idx in range(points))


def build_simulation_sweep_plan(
    *,
    circuit: CircuitDefinition,
    axes: Sequence[SimulationSweepAxis],
) -> SimulationSweepPlan:
    """Expand one normalized sweep setup into Cartesian execution points."""
    if not axes:
        raise ValueError("At least one sweep axis is required.")

    available_targets = {
        target.value_ref: target for target in list_simulation_sweep_targets(circuit)
    }
    normalized_axes: list[SimulationSweepAxis] = []
    seen_targets: set[str] = set()
    for raw_axis in axes:
        target_value_ref = str(raw_axis.target_value_ref).strip()
        if not target_value_ref:
            raise ValueError("Sweep axis target_value_ref is required.")
        if target_value_ref in seen_targets:
            raise ValueError(f"Duplicate sweep target '{target_value_ref}' is not allowed.")
        if target_value_ref not in available_targets:
            raise ValueError(
                f"Sweep target '{target_value_ref}' is not available in components[*].value_ref."
            )
        values = tuple(float(value) for value in raw_axis.values)
        if not values:
            raise ValueError(f"Sweep axis '{target_value_ref}' has no values.")
        seen_targets.add(target_value_ref)
        normalized_axes.append(
            SimulationSweepAxis(
                target_value_ref=target_value_ref,
                values=values,
                unit=str(raw_axis.unit or available_targets[target_value_ref].unit),
            )
        )

    axes_tuple = tuple(normalized_axes)
    grid_ranges = [range(len(axis.values)) for axis in axes_tuple]
    points: list[SimulationSweepPoint] = []
    for point_index, axis_indices in enumerate(product(*grid_ranges)):
        overrides = {
            axis.target_value_ref: float(axis.values[value_index])
            for axis, value_index in zip(axes_tuple, axis_indices, strict=True)
        }
        points.append(
            SimulationSweepPoint(
                point_index=point_index,
                axis_indices=tuple(int(value) for value in axis_indices),
                value_ref_overrides=overrides,
            )
        )
    if not points:
        raise ValueError("Sweep plan generated zero points.")
    return SimulationSweepPlan(axes=axes_tuple, points=tuple(points))


def simulation_sweep_setup_snapshot(plan: SimulationSweepPlan) -> dict[str, Any]:
    """Serialize one sweep plan into a stable setup snapshot payload."""
    return {
        "dimensions": int(plan.dimension),
        "point_count": int(plan.point_count),
        "axes": [
            {
                "target_value_ref": axis.target_value_ref,
                "unit": axis.unit,
                "values": [float(value) for value in axis.values],
            }
            for axis in plan.axes
        ],
    }


def apply_simulation_sweep_overrides(
    *,
    circuit: CircuitDefinition,
    value_ref_overrides: Mapping[str, float],
) -> CircuitDefinition:
    """Build one concrete circuit by overriding selected `components[*].value_ref` defaults."""
    if not value_ref_overrides:
        return circuit

    available_targets = {target.value_ref for target in list_simulation_sweep_targets(circuit)}
    unknown_targets = sorted(set(value_ref_overrides) - available_targets)
    if unknown_targets:
        raise ValueError(f"Unknown sweep target(s): {', '.join(unknown_targets)}.")

    expanded = circuit.expanded_definition
    normalized_overrides = {str(key): float(value) for key, value in value_ref_overrides.items()}
    source_payload = {
        "name": expanded.name,
        "components": [
            _resolved_component_payload(
                component=component,
                expanded=expanded,
                value_ref_overrides=normalized_overrides,
            )
            for component in expanded.components
        ],
        "topology": [row.as_tuple() for row in expanded.topology],
    }
    return CircuitDefinition.model_validate(source_payload)


def run_parameter_sweep(
    *,
    circuit: CircuitDefinition,
    freq_range: FrequencyRange,
    config: SimulationConfig | None,
    plan: SimulationSweepPlan,
) -> SimulationSweepRun:
    """Execute one sweep plan sequentially and return structured point results."""
    if config is None:
        config = SimulationConfig()
    if plan.point_count < 1:
        raise ValueError("Sweep plan must include at least one point.")

    simulator = JuliaSimulator()
    point_results: list[SimulationSweepPointResult] = []
    for point in plan.points:
        swept_circuit = apply_simulation_sweep_overrides(
            circuit=circuit,
            value_ref_overrides=point.value_ref_overrides,
        )
        result = simulator.run_hbsolve(swept_circuit, freq_range, config)
        point_results.append(
            SimulationSweepPointResult(
                point_index=int(point.point_index),
                axis_indices=tuple(point.axis_indices),
                axis_values=dict(point.value_ref_overrides),
                result=result,
            )
        )
    return SimulationSweepRun(
        axes=plan.axes,
        points=tuple(point_results),
        representative_point_index=0,
    )


def simulation_sweep_run_to_payload(run: SimulationSweepRun) -> dict[str, Any]:
    """Serialize one sweep run into a JSON-compatible payload."""
    return {
        "run_kind": "parameter_sweep",
        "dimensions": int(run.dimension),
        "point_count": int(run.point_count),
        "representative_point_index": int(run.representative_point_index),
        "sweep_axes": [
            {
                "target_value_ref": axis.target_value_ref,
                "unit": axis.unit,
                "values": [float(value) for value in axis.values],
            }
            for axis in run.axes
        ],
        "points": [
            {
                "point_index": int(point.point_index),
                "axis_indices": [int(value) for value in point.axis_indices],
                "axis_values": {
                    str(target): float(value) for target, value in sorted(point.axis_values.items())
                },
                "result": point.result.model_dump(mode="json"),
            }
            for point in run.points
        ],
    }


def simulation_sweep_run_from_payload(payload: Mapping[str, Any]) -> SimulationSweepRun:
    """Deserialize one cached/persisted sweep payload."""
    if str(payload.get("run_kind", "")) != "parameter_sweep":
        raise ValueError("Payload is not a parameter sweep result.")

    raw_axes = payload.get("sweep_axes")
    raw_points = payload.get("points")
    if not isinstance(raw_axes, list) or not raw_axes:
        raise ValueError("Sweep payload must include non-empty sweep_axes.")
    if not isinstance(raw_points, list) or not raw_points:
        raise ValueError("Sweep payload must include non-empty points.")

    axes: list[SimulationSweepAxis] = []
    for raw_axis in raw_axes:
        if not isinstance(raw_axis, Mapping):
            raise ValueError("Sweep axis payload is invalid.")
        target_value_ref = str(raw_axis.get("target_value_ref", "")).strip()
        if not target_value_ref:
            raise ValueError("Sweep axis target_value_ref is required.")
        values = raw_axis.get("values")
        if not isinstance(values, list) or not values:
            raise ValueError(f"Sweep axis '{target_value_ref}' has invalid values.")
        axes.append(
            SimulationSweepAxis(
                target_value_ref=target_value_ref,
                unit=str(raw_axis.get("unit", "")),
                values=tuple(float(value) for value in values),
            )
        )

    points: list[SimulationSweepPointResult] = []
    for raw_point in raw_points:
        if not isinstance(raw_point, Mapping):
            raise ValueError("Sweep point payload is invalid.")
        raw_result = raw_point.get("result")
        if not isinstance(raw_result, Mapping):
            raise ValueError("Sweep point result payload is invalid.")
        raw_axis_values = raw_point.get("axis_values", {})
        if not isinstance(raw_axis_values, Mapping):
            raise ValueError("Sweep point axis_values payload is invalid.")
        points.append(
            SimulationSweepPointResult(
                point_index=int(raw_point.get("point_index", len(points))),
                axis_indices=tuple(
                    int(value)
                    for value in (
                        raw_point.get("axis_indices", [])
                        if isinstance(raw_point.get("axis_indices", []), list)
                        else []
                    )
                ),
                axis_values={
                    str(target): float(value) for target, value in raw_axis_values.items()
                },
                result=SimulationResult.model_validate(raw_result),
            )
        )

    representative_point_index = int(payload.get("representative_point_index", 0))
    return SimulationSweepRun(
        axes=tuple(axes),
        points=tuple(points),
        representative_point_index=representative_point_index,
    )


def _resolved_component_payload(
    *,
    component: ComponentSpec,
    expanded: ExpandedCircuitDefinition,
    value_ref_overrides: Mapping[str, float],
) -> dict[str, Any]:
    """Resolve one expanded component row into a direct numeric component payload."""
    if component.default is not None:
        resolved_value = float(component.default)
    elif component.value_ref is not None:
        parameter = expanded.parameter_spec(component.value_ref)
        if parameter is None:
            raise ValueError(f"Undefined parameter '{component.value_ref}' in expanded circuit.")
        resolved_value = float(value_ref_overrides.get(component.value_ref, parameter.default))
    else:
        raise ValueError(f"Component '{component.name}' has neither default nor value_ref.")

    return {
        "name": component.name,
        "default": resolved_value,
        "unit": component.unit,
    }
