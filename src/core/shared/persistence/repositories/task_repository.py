"""Repository for TaskRecord lifecycle operations."""

from __future__ import annotations

from collections.abc import Sequence
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import desc, or_
from sqlmodel import Session, col, select

from core.shared.persistence.models import TaskRecord

_ACTIVE_TASK_STATUSES = ("queued", "running")


def _utcnow() -> datetime:
    """Return one naive UTC timestamp without using deprecated utcnow()."""
    return datetime.now(UTC).replace(tzinfo=None)


def _normalize_status_filter(
    status_filter: str | Sequence[str] | None,
) -> list[str]:
    """Normalize optional task-status filters into concrete strings."""
    if status_filter is None:
        return []
    if isinstance(status_filter, str):
        normalized = status_filter.strip()
        return [normalized] if normalized else []
    return [status.strip() for status in status_filter if status.strip()]


class TaskRepository:
    """Repository for persisted task lifecycle state."""

    def __init__(self, session: Session):
        self._session = session

    def _require_task(self, task_id: int) -> TaskRecord:
        task = self._session.get(TaskRecord, task_id)
        if task is None:
            raise ValueError(f"Task ID {task_id} not found.")
        return task

    def create_task(
        self,
        task_kind: str,
        design_id: int,
        request_payload: dict[str, Any],
        requested_by: str,
        *,
        actor_id: int | None = None,
        dedupe_key: str | None = None,
        trace_batch_id: int | None = None,
        analysis_run_id: int | None = None,
    ) -> TaskRecord:
        """Create and flush one queued task record."""
        task = TaskRecord(
            task_kind=task_kind,
            status="queued",
            design_id=design_id,
            trace_batch_id=trace_batch_id,
            analysis_run_id=analysis_run_id,
            requested_by=requested_by,
            actor_id=actor_id,
            dedupe_key=dedupe_key,
            request_payload=dict(request_payload),
        )
        self._session.add(task)
        self._session.flush()
        return task

    def mark_running(self, task_id: int) -> None:
        """Mark one task as running and stamp start/heartbeat timestamps."""
        task = self._require_task(task_id)
        now = _utcnow()
        task.status = "running"
        task.started_at = now
        task.heartbeat_at = now
        self._session.add(task)
        self._session.flush()

    def heartbeat(self, task_id: int, progress_payload: dict[str, Any]) -> None:
        """Persist one task heartbeat and progress snapshot."""
        task = self._require_task(task_id)
        task.heartbeat_at = _utcnow()
        task.progress_payload = dict(progress_payload)
        self._session.add(task)
        self._session.flush()

    def mark_completed(
        self,
        task_id: int,
        trace_batch_id: int | None,
        result_summary_payload: dict[str, Any],
        *,
        analysis_run_id: int | None = None,
    ) -> None:
        """Mark one task as completed and link its persisted outputs."""
        task = self._require_task(task_id)
        now = _utcnow()
        task.status = "completed"
        task.trace_batch_id = trace_batch_id
        task.analysis_run_id = analysis_run_id
        task.result_summary_payload = dict(result_summary_payload)
        task.error_payload = {}
        task.completed_at = now
        task.heartbeat_at = now
        self._session.add(task)
        self._session.flush()

    def mark_failed(self, task_id: int, error_payload: dict[str, Any]) -> None:
        """Mark one task as failed and persist structured error details."""
        task = self._require_task(task_id)
        now = _utcnow()
        task.status = "failed"
        task.error_payload = dict(error_payload)
        task.completed_at = now
        task.heartbeat_at = now
        self._session.add(task)
        self._session.flush()

    def get_task(self, task_id: int) -> TaskRecord | None:
        """Load one task by ID."""
        return self._session.get(TaskRecord, task_id)

    def list_tasks_by_design(
        self,
        design_id: int,
        status_filter: str | Sequence[str] | None = None,
    ) -> list[TaskRecord]:
        """List tasks for one design, newest first, with optional status filter."""
        statement = select(TaskRecord).where(col(TaskRecord.design_id) == design_id)
        normalized_statuses = _normalize_status_filter(status_filter)
        if normalized_statuses:
            statement = statement.where(col(TaskRecord.status).in_(normalized_statuses))
        statement = statement.order_by(desc(col(TaskRecord.created_at)), desc(col(TaskRecord.id)))
        return list(self._session.exec(statement).all())

    def get_latest_task_by_kind(self, design_id: int, task_kind: str) -> TaskRecord | None:
        """Get the newest task of one kind under one design."""
        statement = (
            select(TaskRecord)
            .where(col(TaskRecord.design_id) == design_id)
            .where(col(TaskRecord.task_kind) == task_kind)
            .order_by(desc(col(TaskRecord.created_at)), desc(col(TaskRecord.id)))
        )
        return self._session.exec(statement).first()

    def find_active_by_dedupe_key(self, dedupe_key: str) -> TaskRecord | None:
        """Find one queued/running task by its dedupe key."""
        normalized_key = dedupe_key.strip()
        if not normalized_key:
            return None
        statement = (
            select(TaskRecord)
            .where(col(TaskRecord.dedupe_key) == normalized_key)
            .where(col(TaskRecord.status).in_(_ACTIVE_TASK_STATUSES))
            .order_by(desc(col(TaskRecord.created_at)), desc(col(TaskRecord.id)))
        )
        return self._session.exec(statement).first()

    def find_active_for_trace_batch(self, trace_batch_id: int) -> TaskRecord | None:
        """Find one queued/running task linked to a specific trace batch."""
        statement = (
            select(TaskRecord)
            .where(col(TaskRecord.trace_batch_id) == trace_batch_id)
            .where(col(TaskRecord.status).in_(_ACTIVE_TASK_STATUSES))
            .order_by(desc(col(TaskRecord.created_at)), desc(col(TaskRecord.id)))
        )
        return self._session.exec(statement).first()

    def list_stale_running_tasks(self, before_heartbeat_at: datetime) -> list[TaskRecord]:
        """List running tasks whose heartbeat is missing or older than the threshold."""
        statement = (
            select(TaskRecord)
            .where(col(TaskRecord.status) == "running")
            .where(
                or_(
                    col(TaskRecord.heartbeat_at).is_(None),
                    col(TaskRecord.heartbeat_at) < before_heartbeat_at,
                )
            )
            .order_by(col(TaskRecord.heartbeat_at), col(TaskRecord.id))
        )
        return list(self._session.exec(statement).all())
