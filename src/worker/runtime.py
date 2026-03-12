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
    TaskExecutionResult,
    WorkerExecutionProvenance,
    audit_action_for_phase,
    build_task_completed_mutation,
    build_task_crash_payload,
    build_task_failed_mutation,
    build_task_failure_payload,
    build_task_running_mutation,
    build_task_start_payload,
    build_task_success_payload,
    build_worker_audit_payload,
    build_worker_audit_summary,
    build_worker_execution_provenance,
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


def _worker_provenance(
    *,
    lane_name: LaneName,
    worker_task_name: WorkerTaskName,
    started_at: datetime | None = None,
    completed_at: datetime | None = None,
    crash_requested_at: datetime | None = None,
) -> WorkerExecutionProvenance:
    """Build canonical worker provenance for one runtime lifecycle event."""
    return build_worker_execution_provenance(
        lane=lane_name,
        worker_task_name=worker_task_name,
        worker_pid=os.getpid(),
        started_at=started_at,
        completed_at=completed_at,
        crash_requested_at=crash_requested_at,
    )


def execute_managed_task(
    *,
    task_id: int,
    lane_name: LaneName,
    worker_task_name: WorkerTaskName,
    operation: Callable[[], TaskExecutionResult],
) -> dict[str, object]:
    """Run one managed worker operation and persist its lifecycle into TaskRecord."""
    running_at = _utcnow()
    running_provenance = _worker_provenance(
        lane_name=lane_name,
        worker_task_name=worker_task_name,
        started_at=running_at,
    )
    with get_unit_of_work() as uow:
        task = uow.tasks.get_task(task_id)
        if task is None:
            raise ValueError(f"Task ID {task_id} not found.")
        actor_id = task.actor_id
        uow.tasks.apply_lifecycle_mutation(
            task_id,
            build_task_running_mutation(
                recorded_at=running_at,
                progress_payload=build_task_start_payload(provenance=running_provenance),
            ),
        )
        uow.audit_logs.append_log(
            actor_id=actor_id,
            action_kind=audit_action_for_phase("running"),
            resource_kind="task",
            resource_id=task_id,
            summary=build_worker_audit_summary(
                phase="running",
                worker_task_name=worker_task_name,
                task_id=task_id,
            ),
            payload=build_worker_audit_payload(
                phase="running",
                provenance=running_provenance,
            ),
        )
        uow.commit()

    try:
        result = operation()
    except Exception as exc:
        failed_at = _utcnow()
        failure_provenance = _worker_provenance(
            lane_name=lane_name,
            worker_task_name=worker_task_name,
        )
        failure_payload = build_task_failure_payload(
            provenance=failure_provenance,
            exc_type=type(exc).__name__,
            message=str(exc),
        )
        with get_unit_of_work() as uow:
            task = uow.tasks.get_task(task_id)
            actor_id = task.actor_id if task is not None else None
            uow.tasks.apply_lifecycle_mutation(
                task_id,
                build_task_failed_mutation(
                    recorded_at=failed_at,
                    error_payload=failure_payload,
                ),
            )
            uow.audit_logs.append_log(
                actor_id=actor_id,
                action_kind=audit_action_for_phase("failed"),
                resource_kind="task",
                resource_id=task_id,
                summary=build_worker_audit_summary(
                    phase="failed",
                    worker_task_name=worker_task_name,
                    task_id=task_id,
                ),
                payload=failure_payload,
            )
            uow.commit()
        return failure_payload

    completed_at = _utcnow()
    completed_provenance = _worker_provenance(
        lane_name=lane_name,
        worker_task_name=worker_task_name,
        completed_at=completed_at,
    )
    completed_payload = build_task_success_payload(
        provenance=completed_provenance,
        summary_payload=dict(result.result_summary_payload),
        result_handle=result.result_handle(),
    )
    with get_unit_of_work() as uow:
        task = uow.tasks.get_task(task_id)
        actor_id = task.actor_id if task is not None else None
        uow.tasks.apply_lifecycle_mutation(
            task_id,
            build_task_completed_mutation(
                recorded_at=completed_at,
                result_summary_payload=completed_payload,
                result_handle=result.result_handle(),
            ),
        )
        uow.audit_logs.append_log(
            actor_id=actor_id,
            action_kind=audit_action_for_phase("completed"),
            resource_kind="task",
            resource_id=task_id,
            summary=build_worker_audit_summary(
                phase="completed",
                worker_task_name=worker_task_name,
                task_id=task_id,
            ),
            payload=completed_payload,
        )
        uow.commit()
    return completed_payload


def mark_task_running_before_crash(
    *,
    task_id: int,
    lane_name: LaneName,
    worker_task_name: WorkerTaskName,
) -> None:
    """Persist a running state immediately before an intentional worker crash."""
    crash_requested_at = _utcnow()
    crash_provenance = _worker_provenance(
        lane_name=lane_name,
        worker_task_name=worker_task_name,
        crash_requested_at=crash_requested_at,
    )
    with get_unit_of_work() as uow:
        task = uow.tasks.get_task(task_id)
        if task is None:
            raise ValueError(f"Task ID {task_id} not found.")
        actor_id = task.actor_id
        uow.tasks.apply_lifecycle_mutation(
            task_id,
            build_task_running_mutation(
                recorded_at=crash_requested_at,
                progress_payload=build_task_crash_payload(provenance=crash_provenance),
            ),
        )
        uow.audit_logs.append_log(
            actor_id=actor_id,
            action_kind=audit_action_for_phase("crashing"),
            resource_kind="task",
            resource_id=task_id,
            summary=build_worker_audit_summary(
                phase="crashing",
                worker_task_name=worker_task_name,
                task_id=task_id,
            ),
            payload=build_worker_audit_payload(
                phase="crashing",
                provenance=crash_provenance,
            ),
        )
        uow.commit()


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
