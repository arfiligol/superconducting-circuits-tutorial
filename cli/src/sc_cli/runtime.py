"""Read-only runtime accessors for the backend public CLI facade."""

from sc_backend import (
    get_circuit_definition,
    get_session,
    get_task,
    list_datasets,
    list_tasks,
    reset_runtime_state,
    set_active_dataset,
    submit_task,
)

__all__ = [
    "get_circuit_definition",
    "get_session",
    "get_task",
    "list_datasets",
    "list_tasks",
    "reset_runtime_state",
    "set_active_dataset",
    "submit_task",
]
