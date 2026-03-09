"""Shared worker-lane runtime helpers."""

from __future__ import annotations

import argparse
import os
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from typing import Any, Protocol

from core.shared.persistence.reconcile import ReconcileSummary, reconcile_stale_tasks_and_batches
from core.shared.persistence.unit_of_work import get_unit_of_work
from worker.config import LaneName


def _utcnow() -> datetime:
    """Return one naive UTC timestamp without using deprecated utcnow()."""
    return datetime.now(UTC).replace(tzinfo=None)


@dataclass(frozen=True)
class TaskExecutionResult:
    """Persisted worker-task outcome metadata."""

    result_summary_payload: dict[str, Any] = field(default_factory=dict)
    trace_batch_id: int | None = None
    analysis_run_id: int | None = None


class HueyLike(Protocol):
    """Small protocol for Huey objects used by the custom lane consumer."""

    def dequeue(self) -> object | None: ...

    def execute(self, task: object) -> object | None: ...


def _task_start_payload(*, lane_name: LaneName, worker_task_name: str) -> dict[str, Any]:
    """Return progress payload stored when a worker starts one task."""
    return {
        "lane": lane_name,
        "phase": "running",
        "worker_task_name": worker_task_name,
        "worker_pid": os.getpid(),
        "started_at": _utcnow().isoformat(),
    }


def _task_success_payload(
    *,
    lane_name: LaneName,
    worker_task_name: str,
    summary_payload: dict[str, Any],
) -> dict[str, Any]:
    """Return one completed-task summary payload."""
    return {
        **summary_payload,
        "lane": lane_name,
        "worker_task_name": worker_task_name,
        "worker_pid": os.getpid(),
        "completed_at": _utcnow().isoformat(),
    }


def _task_error_payload(
    *,
    lane_name: LaneName,
    worker_task_name: str,
    exc: Exception,
) -> dict[str, Any]:
    """Return one structured task failure payload."""
    return {
        "error_code": "worker_task_failed",
        "summary": f"{worker_task_name} failed in the {lane_name} lane.",
        "details": {
            "lane": lane_name,
            "worker_task_name": worker_task_name,
            "worker_pid": os.getpid(),
            "exception_type": type(exc).__name__,
            "message": str(exc),
        },
    }


def execute_managed_task(
    *,
    task_id: int,
    lane_name: LaneName,
    worker_task_name: str,
    operation: Callable[[], TaskExecutionResult],
) -> dict[str, Any]:
    """Run one managed worker operation and persist its lifecycle into TaskRecord."""
    with get_unit_of_work() as uow:
        task = uow.tasks.get_task(task_id)
        if task is None:
            raise ValueError(f"Task ID {task_id} not found.")
        actor_id = task.actor_id
        uow.tasks.mark_running(task_id)
        uow.tasks.heartbeat(
            task_id,
            _task_start_payload(lane_name=lane_name, worker_task_name=worker_task_name),
        )
        uow.audit_logs.append_log(
            actor_id=actor_id,
            action_kind="worker.task_started",
            resource_kind="task",
            resource_id=task_id,
            summary=f"Worker started {worker_task_name} for task {task_id}",
            payload={"lane": lane_name, "worker_pid": os.getpid()},
        )
        uow.commit()

    try:
        result = operation()
    except Exception as exc:
        failure_payload = _task_error_payload(
            lane_name=lane_name,
            worker_task_name=worker_task_name,
            exc=exc,
        )
        with get_unit_of_work() as uow:
            task = uow.tasks.get_task(task_id)
            actor_id = task.actor_id if task is not None else None
            uow.tasks.mark_failed(task_id, failure_payload)
            uow.audit_logs.append_log(
                actor_id=actor_id,
                action_kind="worker.task_failed",
                resource_kind="task",
                resource_id=task_id,
                summary=f"Worker failed {worker_task_name} for task {task_id}",
                payload=failure_payload,
            )
            uow.commit()
        return failure_payload

    completed_payload = _task_success_payload(
        lane_name=lane_name,
        worker_task_name=worker_task_name,
        summary_payload=dict(result.result_summary_payload),
    )
    with get_unit_of_work() as uow:
        task = uow.tasks.get_task(task_id)
        actor_id = task.actor_id if task is not None else None
        uow.tasks.mark_completed(
            task_id,
            result.trace_batch_id,
            completed_payload,
            analysis_run_id=result.analysis_run_id,
        )
        uow.audit_logs.append_log(
            actor_id=actor_id,
            action_kind="worker.task_completed",
            resource_kind="task",
            resource_id=task_id,
            summary=f"Worker completed {worker_task_name} for task {task_id}",
            payload=completed_payload,
        )
        uow.commit()
    return completed_payload


def mark_task_running_before_crash(
    *,
    task_id: int,
    lane_name: LaneName,
    worker_task_name: str,
) -> None:
    """Persist a running state immediately before an intentional worker crash."""
    with get_unit_of_work() as uow:
        task = uow.tasks.get_task(task_id)
        if task is None:
            raise ValueError(f"Task ID {task_id} not found.")
        actor_id = task.actor_id
        uow.tasks.mark_running(task_id)
        uow.tasks.heartbeat(
            task_id,
            {
                "lane": lane_name,
                "phase": "crashing",
                "worker_task_name": worker_task_name,
                "worker_pid": os.getpid(),
                "crash_requested_at": _utcnow().isoformat(),
            },
        )
        uow.audit_logs.append_log(
            actor_id=actor_id,
            action_kind="worker.task_crashing",
            resource_kind="task",
            resource_id=task_id,
            summary=f"Worker is about to crash while running {worker_task_name} for task {task_id}",
            payload={"lane": lane_name, "worker_pid": os.getpid()},
        )
        uow.commit()


def reconcile_stale_worker_tasks(*, stale_after_seconds: int) -> ReconcileSummary:
    """Run the WS2 reconcile path with a worker-friendly timeout."""
    stale_before = _utcnow() - timedelta(seconds=stale_after_seconds)
    with get_unit_of_work() as uow:
        return reconcile_stale_tasks_and_batches(uow, stale_before=stale_before)


def consume_queued_tasks(
    huey: HueyLike,
    *,
    lane_name: LaneName,
    max_tasks: int | None,
    idle_timeout: float,
    poll_interval: float,
    reconcile_stale_after_seconds: int | None = None,
) -> int:
    """Consume queued Huey tasks serially for one worker lane."""
    if reconcile_stale_after_seconds is not None:
        reconcile_stale_worker_tasks(stale_after_seconds=reconcile_stale_after_seconds)

    processed = 0
    idle_deadline = time.monotonic() + max(0.0, idle_timeout)
    while max_tasks is None or processed < max_tasks:
        task = huey.dequeue()
        if task is None:
            if time.monotonic() >= idle_deadline:
                break
            time.sleep(max(0.01, poll_interval))
            continue

        idle_deadline = time.monotonic() + max(0.0, idle_timeout)
        huey.execute(task)
        processed += 1

    return processed


def build_consumer_parser(*, lane_name: LaneName) -> argparse.ArgumentParser:
    """Build a tiny CLI parser for one lane-specific consumer."""
    parser = argparse.ArgumentParser(
        prog=f"sc-worker-{lane_name}",
        description=f"Run the {lane_name} worker lane consumer.",
    )
    parser.add_argument("--max-tasks", type=int, default=None)
    parser.add_argument("--idle-timeout", type=float, default=5.0)
    parser.add_argument("--poll-interval", type=float, default=0.25)
    parser.add_argument("--reconcile-stale-seconds", type=int, default=None)
    return parser
