"""Persisted task/result recovery helpers for the WS6 simulation page."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime

from app.api.schemas import DesignTasksResponse, LatestTraceBatchResponse, TaskResponse

_LONG_RUNNING_WARN_AFTER_SECONDS = 60


def _utcnow() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None)


@dataclass(frozen=True)
class SimulationRecoveryState:
    """Recovered persisted simulation authority for one design."""

    task: TaskResponse | None
    latest_result: LatestTraceBatchResponse | None
    should_poll: bool
    long_running_warning: bool


def latest_simulation_task(tasks_response: DesignTasksResponse) -> TaskResponse | None:
    """Return the newest simulation task from one design-task listing."""
    for task in tasks_response.tasks:
        if task.task_kind == "simulation":
            return task
    return None


def build_recovery_state(
    *,
    tasks_response: DesignTasksResponse,
    latest_result: LatestTraceBatchResponse | None,
    now: datetime | None = None,
) -> SimulationRecoveryState:
    """Resolve polling/recovery authority for one simulation page refresh."""
    task = latest_simulation_task(tasks_response)
    current_now = now or _utcnow()
    should_poll = task is not None and task.status in {"queued", "running"}
    long_running_warning = False
    if task is not None and task.status == "running" and task.started_at is not None:
        elapsed = (current_now - task.started_at).total_seconds()
        long_running_warning = elapsed >= _LONG_RUNNING_WARN_AFTER_SECONDS
    return SimulationRecoveryState(
        task=task,
        latest_result=latest_result,
        should_poll=should_poll,
        long_running_warning=long_running_warning,
    )
