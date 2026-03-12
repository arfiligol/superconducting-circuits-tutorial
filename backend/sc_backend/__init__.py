"""Public backend-facing surface for non-HTTP consumers such as the CLI."""

from src.app.api.schemas.circuit_definitions import (
    CircuitDefinitionDetailResponse,
    CircuitDefinitionSummaryResponse,
)
from src.app.api.schemas.datasets import DatasetSummaryResponse
from src.app.api.schemas.errors import ApiErrorBodyResponse
from src.app.api.schemas.session import SessionResponse
from src.app.api.schemas.tasks import TaskDetailResponse, TaskSummaryResponse
from src.app.domain.circuit_definitions import CircuitDefinitionSortBy
from src.app.domain.datasets import DatasetSortBy, DatasetStatus, SortOrder
from src.app.domain.tasks import TaskKind, TaskLane, TaskStatus, TaskVisibilityScope

from sc_backend.errors import BackendContractError
from sc_backend.rewrite_cli import (
    create_circuit_definition,
    delete_circuit_definition,
    get_circuit_definition,
    get_session,
    get_task,
    list_circuit_definitions,
    list_datasets,
    list_tasks,
    reset_runtime_state,
    set_active_dataset,
    submit_task,
    update_circuit_definition,
)

__all__ = [
    "ApiErrorBodyResponse",
    "BackendContractError",
    "CircuitDefinitionDetailResponse",
    "CircuitDefinitionSortBy",
    "CircuitDefinitionSummaryResponse",
    "DatasetSortBy",
    "DatasetStatus",
    "DatasetSummaryResponse",
    "SessionResponse",
    "SortOrder",
    "TaskDetailResponse",
    "TaskKind",
    "TaskLane",
    "TaskStatus",
    "TaskSummaryResponse",
    "TaskVisibilityScope",
    "create_circuit_definition",
    "delete_circuit_definition",
    "get_circuit_definition",
    "get_session",
    "get_task",
    "list_circuit_definitions",
    "list_datasets",
    "list_tasks",
    "reset_runtime_state",
    "set_active_dataset",
    "submit_task",
    "update_circuit_definition",
]
