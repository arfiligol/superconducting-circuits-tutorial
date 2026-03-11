"""Persisted task/result recovery helpers for the WS6 simulation page."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime

from app.api.schemas import DesignTasksResponse, LatestTraceBatchResponse, TaskResponse

_LONG_RUNNING_WARN_AFTER_SECONDS = 60


def _utcnow() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None)


@dataclass(frozen=True)
class TaskRecoveryState:
    """Recovered persisted task authority for one design and task kind."""

    task: TaskResponse | None
    should_poll: bool
    long_running_warning: bool


@dataclass(frozen=True)
class SimulationRecoveryState:
    """Recovered persisted simulation authority for one design."""

    task: TaskResponse | None
    latest_result: LatestTraceBatchResponse | None
    should_poll: bool
    long_running_warning: bool


def latest_task_by_kind(
    tasks_response: DesignTasksResponse,
    *,
    task_kind: str,
) -> TaskResponse | None:
    """Return the newest task of one kind from one design-task listing."""
    for task in tasks_response.tasks:
        if task.task_kind == task_kind:
            return task
    return None


def latest_simulation_task(tasks_response: DesignTasksResponse) -> TaskResponse | None:
    """Return the newest simulation task from one design-task listing."""
    return latest_task_by_kind(tasks_response, task_kind="simulation")


def latest_post_processing_task(tasks_response: DesignTasksResponse) -> TaskResponse | None:
    """Return the newest post-processing task from one design-task listing."""
    return latest_task_by_kind(tasks_response, task_kind="post_processing")


def build_task_recovery_state(
    *,
    tasks_response: DesignTasksResponse,
    task_kind: str,
    now: datetime | None = None,
) -> TaskRecoveryState:
    """Resolve polling/recovery authority for one task kind on page refresh."""
    task = latest_task_by_kind(tasks_response, task_kind=task_kind)
    current_now = now or _utcnow()
    should_poll = task is not None and task.status in {"queued", "running"}
    long_running_warning = False
    if task is not None and task.status == "running" and task.started_at is not None:
        elapsed = (current_now - task.started_at).total_seconds()
        long_running_warning = elapsed >= _LONG_RUNNING_WARN_AFTER_SECONDS
    return TaskRecoveryState(
        task=task,
        should_poll=should_poll,
        long_running_warning=long_running_warning,
    )


def build_recovery_state(
    *,
    tasks_response: DesignTasksResponse,
    latest_result: LatestTraceBatchResponse | None,
    now: datetime | None = None,
) -> SimulationRecoveryState:
    """Resolve polling/recovery authority for one simulation page refresh."""
    task_state = build_task_recovery_state(
        tasks_response=tasks_response,
        task_kind="simulation",
        now=now,
    )
    return SimulationRecoveryState(
        task=task_state.task,
        latest_result=latest_result,
        should_poll=task_state.should_poll,
        long_running_warning=task_state.long_running_warning,
    )
