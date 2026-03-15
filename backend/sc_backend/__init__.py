"""Public backend-facing surface for non-HTTP consumers such as the CLI.

The facade stays import-safe even when unrelated backend adapters drift, so CLI
test collection can load command modules without eagerly importing every
runtime implementation.
"""

from __future__ import annotations

from typing import Literal

from src.app.api.schemas.circuit_definitions import (
    CircuitDefinitionDetailResponse,
    CircuitDefinitionSummaryResponse,
)
from src.app.api.schemas.datasets import (
    DatasetDetailResponse,
    DatasetMetadataUpdateResponse,
    DatasetSummaryResponse,
)
from src.app.api.schemas.errors import ApiErrorBodyResponse
from src.app.api.schemas.session import SessionResponse
from src.app.api.schemas.tasks import TaskDetailResponse, TaskEventResponse, TaskSummaryResponse
from src.app.domain.circuit_definitions import CircuitDefinitionSortBy, SortOrder
from src.app.domain.datasets import DatasetStatus
from src.app.domain.tasks import TaskKind, TaskLane, TaskStatus, TaskVisibilityScope

from sc_backend.errors import BackendContractError

# Compatibility shim for CLI imports. The current backend dataset domain no
# longer exports dataset sort literals directly, but CLI command modules still
# type against this public facade.
DatasetSortBy = Literal["updated_at", "name", "samples"]


def create_circuit_definition(*args: object, **kwargs: object):
    from sc_backend.rewrite_cli import create_circuit_definition as _create_circuit_definition

    return _create_circuit_definition(*args, **kwargs)


def delete_circuit_definition(*args: object, **kwargs: object):
    from sc_backend.rewrite_cli import delete_circuit_definition as _delete_circuit_definition

    return _delete_circuit_definition(*args, **kwargs)


def get_circuit_definition(*args: object, **kwargs: object):
    from sc_backend.rewrite_cli import get_circuit_definition as _get_circuit_definition

    return _get_circuit_definition(*args, **kwargs)


def get_dataset(*args: object, **kwargs: object):
    from sc_backend.rewrite_cli import get_dataset as _get_dataset

    return _get_dataset(*args, **kwargs)


def get_session(*args: object, **kwargs: object):
    from sc_backend.rewrite_cli import get_session as _get_session

    return _get_session(*args, **kwargs)


def get_task(*args: object, **kwargs: object):
    from sc_backend.rewrite_cli import get_task as _get_task

    return _get_task(*args, **kwargs)


def list_circuit_definitions(*args: object, **kwargs: object):
    from sc_backend.rewrite_cli import list_circuit_definitions as _list_circuit_definitions

    return _list_circuit_definitions(*args, **kwargs)


def list_datasets(*args: object, **kwargs: object):
    from sc_backend.rewrite_cli import list_datasets as _list_datasets

    return _list_datasets(*args, **kwargs)


def list_tasks(*args: object, **kwargs: object):
    from sc_backend.rewrite_cli import list_tasks as _list_tasks

    return _list_tasks(*args, **kwargs)


def reset_runtime_state(*args: object, **kwargs: object):
    from sc_backend.rewrite_cli import reset_runtime_state as _reset_runtime_state

    return _reset_runtime_state(*args, **kwargs)


def set_active_dataset(*args: object, **kwargs: object):
    from sc_backend.rewrite_cli import set_active_dataset as _set_active_dataset

    return _set_active_dataset(*args, **kwargs)


def submit_task(*args: object, **kwargs: object):
    from sc_backend.rewrite_cli import submit_task as _submit_task

    return _submit_task(*args, **kwargs)


def update_circuit_definition(*args: object, **kwargs: object):
    from sc_backend.rewrite_cli import update_circuit_definition as _update_circuit_definition

    return _update_circuit_definition(*args, **kwargs)


def update_dataset_metadata(*args: object, **kwargs: object):
    from sc_backend.rewrite_cli import update_dataset_metadata as _update_dataset_metadata

    return _update_dataset_metadata(*args, **kwargs)


__all__ = [
    "ApiErrorBodyResponse",
    "BackendContractError",
    "CircuitDefinitionDetailResponse",
    "CircuitDefinitionSortBy",
    "CircuitDefinitionSummaryResponse",
    "DatasetDetailResponse",
    "DatasetMetadataUpdateResponse",
    "DatasetSortBy",
    "DatasetStatus",
    "DatasetSummaryResponse",
    "SessionResponse",
    "SortOrder",
    "TaskDetailResponse",
    "TaskEventResponse",
    "TaskKind",
    "TaskLane",
    "TaskStatus",
    "TaskSummaryResponse",
    "TaskVisibilityScope",
    "create_circuit_definition",
    "delete_circuit_definition",
    "get_circuit_definition",
    "get_dataset",
    "get_session",
    "get_task",
    "list_circuit_definitions",
    "list_datasets",
    "list_tasks",
    "reset_runtime_state",
    "set_active_dataset",
    "submit_task",
    "update_circuit_definition",
    "update_dataset_metadata",
]
