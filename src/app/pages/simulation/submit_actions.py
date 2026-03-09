"""Shared WS6 simulation submit helpers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.api.schemas import SimulationTaskCreateRequest
from app.services.execution_context import UseCaseContext
from app.services.simulation_task_contract import (
    PersistedSimulationTaskRequest,
    embed_simulation_request,
)
from core.simulation.domain.circuit import CircuitDefinition, FrequencyRange, SimulationConfig


@dataclass(frozen=True)
class PreparedSimulationSubmission:
    """Canonical WS6 simulation submit payload assembled in the page layer."""

    api_request: SimulationTaskCreateRequest
    persisted_request: PersistedSimulationTaskRequest


def build_simulation_submission(
    *,
    design_id: int,
    design_name: str,
    circuit: CircuitDefinition,
    freq_range: FrequencyRange,
    config: SimulationConfig,
    config_snapshot: dict[str, Any],
    source_meta: dict[str, Any],
    schema_source_hash: str,
    simulation_setup_hash: str,
    sweep_setup_payload: dict[str, Any] | None,
    sweep_setup_hash: str | None,
    context: UseCaseContext,
    force_rerun: bool,
) -> PreparedSimulationSubmission:
    """Build the persisted request payload sent to `POST /api/v1/tasks/simulation`."""
    persisted_request = PersistedSimulationTaskRequest(
        design_id=int(design_id),
        design_name=str(design_name),
        circuit_payload=circuit.to_source_payload(),
        freq_range_payload=freq_range.model_dump(mode="json"),
        config_payload=config.model_dump(mode="json"),
        config_snapshot=dict(config_snapshot),
        source_meta=dict(source_meta),
        schema_source_hash=str(schema_source_hash),
        simulation_setup_hash=str(simulation_setup_hash),
        sweep_setup_payload=dict(sweep_setup_payload) if sweep_setup_payload is not None else None,
        sweep_setup_hash=sweep_setup_hash,
        context_payload=context.to_payload(),
    )
    api_request = SimulationTaskCreateRequest(
        design_id=int(design_id),
        schema_source_hash=str(schema_source_hash),
        simulation_setup_hash=str(simulation_setup_hash),
        request_payload=embed_simulation_request({}, persisted_request),
        force_rerun=bool(force_rerun),
    )
    return PreparedSimulationSubmission(
        api_request=api_request,
        persisted_request=persisted_request,
    )
