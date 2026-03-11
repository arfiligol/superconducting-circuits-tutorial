"""Public backend-facing surface for non-HTTP consumers such as the CLI."""

from src.app.api.schemas.circuit_definitions import CircuitDefinitionDetailResponse
from src.app.api.schemas.datasets import DatasetSummaryResponse
from src.app.api.schemas.errors import ApiErrorBodyResponse
from src.app.api.schemas.session import SessionResponse
from src.app.api.schemas.tasks import TaskDetailResponse, TaskSummaryResponse
from src.app.domain.datasets import DatasetSortBy, DatasetStatus, SortOrder
from src.app.domain.tasks import TaskLane, TaskStatus, TaskVisibilityScope

from sc_backend.errors import BackendContractError
from sc_backend.rewrite_cli import (
    get_circuit_definition,
    get_session,
    get_task,
    list_datasets,
    list_tasks,
    reset_runtime_state,
)

__all__ = [
    "ApiErrorBodyResponse",
    "BackendContractError",
    "CircuitDefinitionDetailResponse",
    "DatasetSortBy",
    "DatasetStatus",
    "DatasetSummaryResponse",
    "SessionResponse",
    "SortOrder",
    "TaskDetailResponse",
    "TaskLane",
    "TaskStatus",
    "TaskSummaryResponse",
    "TaskVisibilityScope",
    "get_circuit_definition",
    "get_session",
    "get_task",
    "list_datasets",
    "list_tasks",
    "reset_runtime_state",
]
