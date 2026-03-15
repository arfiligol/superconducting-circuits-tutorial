"""Runtime accessors for standalone local state and legacy facades."""

from contextlib import suppress

from sc_backend import (
    create_circuit_definition,
    delete_circuit_definition,
    get_circuit_definition,
    get_dataset,
    list_circuit_definitions,
    list_datasets,
    update_circuit_definition,
    update_dataset_metadata,
)
from sc_backend import (
    reset_runtime_state as reset_backend_runtime_state,
)

from sc_cli.local_runtime import (
    get_session,
    get_task,
    list_tasks,
    set_active_dataset,
    submit_task,
)
from sc_cli.local_runtime import (
    reset_runtime_state as reset_local_runtime_state,
)


def reset_runtime_state() -> None:
    reset_local_runtime_state()
    with suppress(ImportError):
        reset_backend_runtime_state()


__all__ = [
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
