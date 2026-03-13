"""Shared task-operator helpers for CLI command families."""

from collections.abc import Callable
from enum import Enum
from time import monotonic, sleep

from sc_backend import (
    BackendContractError,
    TaskDetailResponse,
    TaskEventResponse,
    TaskSummaryResponse,
)

from sc_cli.errors import exit_for_backend_error, exit_with_runtime_error
from sc_cli.output import OutputMode

TERMINAL_TASK_STATUSES = {"completed", "failed"}


class TaskStatusOption(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class TaskScopeOption(str, Enum):
    WORKSPACE = "workspace"
    OWNED = "owned"


class WaitStatusOption(str, Enum):
    TERMINAL = "terminal"
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


def get_task_or_exit(
    *,
    task_id: int,
    output: OutputMode,
    get_task_fn: Callable[[int], TaskDetailResponse],
) -> TaskDetailResponse:
    try:
        return get_task_fn(task_id)
    except BackendContractError as error:
        exit_for_backend_error(error, output=output)


def get_lane_task_or_exit(
    *,
    task_id: int,
    lane: str,
    lane_label: str,
    output: OutputMode,
    get_task_fn: Callable[[int], TaskDetailResponse],
) -> TaskDetailResponse:
    task = get_task_or_exit(task_id=task_id, output=output, get_task_fn=get_task_fn)
    if task.lane != lane:
        exit_with_runtime_error(f"Task {task_id} is not part of the {lane_label} lane.")
    return task


def list_tasks_or_exit(
    *,
    output: OutputMode,
    list_tasks_fn: Callable[..., list[TaskSummaryResponse]],
    **filters: object,
) -> list[TaskSummaryResponse]:
    try:
        return list_tasks_fn(**filters)
    except BackendContractError as error:
        exit_for_backend_error(error, output=output)


def latest_task_or_exit(
    *,
    output: OutputMode,
    no_match_message: str,
    get_task_fn: Callable[[int], TaskDetailResponse],
    list_tasks_fn: Callable[..., list[TaskSummaryResponse]],
    **filters: object,
) -> TaskDetailResponse:
    tasks = list_tasks_or_exit(output=output, list_tasks_fn=list_tasks_fn, **filters)
    if not tasks:
        exit_with_runtime_error(no_match_message)
    return get_task_or_exit(task_id=tasks[0].task_id, output=output, get_task_fn=get_task_fn)


def latest_lane_task_or_exit(
    *,
    expected_lane: str,
    lane_label: str,
    output: OutputMode,
    get_task_fn: Callable[[int], TaskDetailResponse],
    list_tasks_fn: Callable[..., list[TaskSummaryResponse]],
    no_match_message: str,
    **filters: object,
) -> TaskDetailResponse:
    task = latest_task_or_exit(
        output=output,
        no_match_message=no_match_message,
        get_task_fn=get_task_fn,
        list_tasks_fn=list_tasks_fn,
        **filters,
    )
    if task.lane != expected_lane:
        exit_with_runtime_error(f"Task {task.task_id} is not part of the {lane_label} lane.")
    return task


def wait_for_task_or_exit(
    *,
    load_task: Callable[[], TaskDetailResponse],
    is_ready: Callable[[TaskDetailResponse], bool],
    timeout_message: str,
    interval: float,
    timeout: float,
) -> TaskDetailResponse:
    deadline = monotonic() + timeout
    while True:
        task = load_task()
        if is_ready(task):
            return task
        if monotonic() >= deadline:
            exit_with_runtime_error(timeout_message)
        sleep(interval)


def has_reached_wait_target(
    *,
    task: TaskDetailResponse,
    until_status: WaitStatusOption,
) -> bool:
    if until_status is WaitStatusOption.TERMINAL:
        return task.status in TERMINAL_TASK_STATUSES
    return task.status == until_status.value


def select_task_events(
    task: TaskDetailResponse,
    *,
    event_type: str | None,
    level: str | None,
    limit: int | None,
) -> list[TaskEventResponse]:
    events = [
        event
        for event in task.events
        if (event_type is None or event.event_type == event_type)
        and (level is None or event.level == level)
    ]
    if limit is None:
        return events
    return events[-limit:]
