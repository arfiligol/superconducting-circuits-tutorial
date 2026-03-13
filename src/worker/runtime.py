"""Shared worker-lane runtime helpers."""

from __future__ import annotations

import argparse
import math
import os
import threading
import time
from collections.abc import Callable
from datetime import UTC, datetime, timedelta

from rq import Queue, SimpleWorker
from rq.timeouts import TimerDeathPenalty
from sc_core.execution import (
    TaskExecutionOperation,
    TaskExecutionResult,
    WorkerExecutionContext,
    build_worker_completed_operation,
    build_worker_crashing_operation,
    build_worker_execution_context,
    build_worker_failed_operation,
    build_worker_running_operation,
)
from sc_core.tasking import WorkerTaskName

from core.shared.persistence.reconcile import ReconcileSummary, reconcile_stale_tasks_and_batches
from core.shared.persistence.unit_of_work import get_unit_of_work
from worker.config import LaneName, ensure_connection_available


class _LaneSimpleWorker(SimpleWorker):
    """RQ SimpleWorker variant that also works in test threads."""

    death_penalty_class = TimerDeathPenalty

    def _install_signal_handlers(self) -> None:
        if threading.current_thread() is threading.main_thread():
            super()._install_signal_handlers()


def _utcnow() -> datetime:
    """Return one naive UTC timestamp without using deprecated utcnow()."""
    return datetime.now(UTC).replace(tzinfo=None)


def _worker_execution_context(
    *,
    lane_name: LaneName,
    worker_task_name: WorkerTaskName,
    worker_pid: int | None = None,
) -> WorkerExecutionContext:
    """Build canonical worker execution context for one runtime process."""
    return build_worker_execution_context(
        lane=lane_name,
        worker_task_name=worker_task_name,
        worker_pid=worker_pid if worker_pid is not None else os.getpid(),
    )


def _persist_execution_operation(operation: TaskExecutionOperation) -> None:
    """Persist one shared orchestration operation and its optional audit record."""
    with get_unit_of_work() as uow:
        uow.tasks.apply_execution_operation(operation)
        uow.audit_logs.append_execution_operation(operation)
        uow.commit()


def execute_managed_task(
    *,
    task_id: int,
    lane_name: LaneName,
    worker_task_name: WorkerTaskName,
    operation: Callable[[], TaskExecutionResult],
) -> dict[str, object]:
    """Run one managed worker operation and persist its lifecycle into TaskRecord."""
    running_at = _utcnow()
    context = _worker_execution_context(
        lane_name=lane_name,
        worker_task_name=worker_task_name,
    )
    with get_unit_of_work() as uow:
        task = uow.tasks.get_task(task_id)
        if task is None:
            raise ValueError(f"Task ID {task_id} not found.")
        actor_id = task.actor_id
    _persist_execution_operation(
        build_worker_running_operation(
            task_id=task_id,
            recorded_at=running_at,
            context=context,
            actor_id=actor_id,
        ),
    )

    try:
        result = operation()
    except Exception as exc:
        failed_at = _utcnow()
        with get_unit_of_work() as uow:
            task = uow.tasks.get_task(task_id)
            actor_id = task.actor_id if task is not None else None
        failed_operation = build_worker_failed_operation(
            task_id=task_id,
            recorded_at=failed_at,
            context=context,
            exc_type=type(exc).__name__,
            message=str(exc),
            actor_id=actor_id,
        )
        _persist_execution_operation(failed_operation)
        return dict(failed_operation.audit_payload or {})

    completed_at = _utcnow()
    with get_unit_of_work() as uow:
        task = uow.tasks.get_task(task_id)
        actor_id = task.actor_id if task is not None else None
    completed_operation = build_worker_completed_operation(
        task_id=task_id,
        recorded_at=completed_at,
        context=context,
        result=result,
        actor_id=actor_id,
    )
    _persist_execution_operation(completed_operation)
    return dict(completed_operation.audit_payload or {})


def mark_task_running_before_crash(
    *,
    task_id: int,
    lane_name: LaneName,
    worker_task_name: WorkerTaskName,
) -> None:
    """Persist a running state immediately before an intentional worker crash."""
    crash_requested_at = _utcnow()
    context = _worker_execution_context(
        lane_name=lane_name,
        worker_task_name=worker_task_name,
    )
    with get_unit_of_work() as uow:
        task = uow.tasks.get_task(task_id)
        if task is None:
            raise ValueError(f"Task ID {task_id} not found.")
        actor_id = task.actor_id
    _persist_execution_operation(
        build_worker_crashing_operation(
            task_id=task_id,
            recorded_at=crash_requested_at,
            context=context,
            actor_id=actor_id,
        ),
    )


def reconcile_stale_worker_tasks(*, stale_after_seconds: int) -> ReconcileSummary:
    """Run the WS2 reconcile path with a worker-friendly timeout."""
    stale_before = _utcnow() - timedelta(seconds=stale_after_seconds)
    with get_unit_of_work() as uow:
        return reconcile_stale_tasks_and_batches(uow, stale_before=stale_before)


def consume_queued_tasks(
    *,
    queue: Queue,
    lane_name: LaneName,
    max_tasks: int | None,
    idle_timeout: float,
    poll_interval: float,
    reconcile_stale_after_seconds: int | None = None,
) -> int:
    """Consume queued RQ jobs serially for one worker lane via SimpleWorker."""
    if reconcile_stale_after_seconds is not None:
        reconcile_stale_worker_tasks(stale_after_seconds=reconcile_stale_after_seconds)

    connection = ensure_connection_available(lane_name)

    if max_tasks is not None and max_tasks <= 0:
        return 0

    worker = _LaneSimpleWorker([queue], connection=connection)
    processed = 0
    idle_deadline = time.monotonic() + max(0.0, idle_timeout)
    while max_tasks is None or processed < max_tasks:
        if int(queue.count) <= 0:
            if time.monotonic() >= idle_deadline:
                break
            time.sleep(max(0.01, poll_interval))
            continue

        queued_before = int(queue.count)
        remaining_jobs = None if max_tasks is None else max_tasks - processed
        worker.work(
            burst=True,
            logging_level="WARNING",
            max_jobs=remaining_jobs,
            max_idle_time=max(1, math.ceil(idle_timeout)),
            with_scheduler=False,
        )
        processed_now = max(0, queued_before - int(queue.count))
        if processed_now <= 0:
            time.sleep(max(0.01, poll_interval))
            continue
        processed += processed_now
        idle_deadline = time.monotonic() + max(0.0, idle_timeout)

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
