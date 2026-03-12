from __future__ import annotations

from typing import cast

from sc_core.tasking import TaskExecutionMode, WorkerTaskName
from sqlalchemy import func, select
from sqlalchemy.orm import Session, sessionmaker

from src.app.domain.tasks import (
    TaskCreateDraft,
    TaskDetail,
    TaskKind,
    TaskLane,
    TaskProgress,
    TaskQueueBackend,
    TaskResultRefs,
    TaskStatus,
    TaskVisibilityScope,
)
from src.app.infrastructure.persistence.models import RewriteTaskRecord


class SqliteRewriteTaskSnapshotRepository:
    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory

    def has_tasks(self) -> bool:
        with self._session_factory() as session:
            return session.scalar(select(func.count(RewriteTaskRecord.id))) != 0

    def list_tasks(self) -> tuple[TaskDetail, ...]:
        with self._session_factory() as session:
            rows = session.scalars(
                select(RewriteTaskRecord).order_by(RewriteTaskRecord.task_id.asc())
            ).all()
            return tuple(_to_task_detail(row) for row in rows)

    def get_task(self, task_id: int) -> TaskDetail | None:
        with self._session_factory() as session:
            row = session.scalar(
                select(RewriteTaskRecord).where(RewriteTaskRecord.task_id == task_id)
            )
            if row is None:
                return None
            return _to_task_detail(row)

    def create_task(self, draft: TaskCreateDraft) -> TaskDetail:
        with self._session_factory() as session:
            next_task_id = session.scalar(select(func.max(RewriteTaskRecord.task_id))) or 305
            row = RewriteTaskRecord(
                task_id=next_task_id + 1,
                kind=draft.kind,
                lane=draft.lane,
                execution_mode=draft.execution_mode,
                status="queued",
                submitted_at="2026-03-12 10:30:00",
                owner_user_id=draft.owner_user_id,
                owner_display_name=draft.owner_display_name,
                workspace_id=draft.workspace_id,
                workspace_slug=draft.workspace_slug,
                visibility_scope=draft.visibility_scope,
                dataset_id=draft.dataset_id,
                definition_id=draft.definition_id,
                summary=draft.summary,
                queue_backend="in_memory_scaffold",
                worker_task_name=draft.worker_task_name,
                request_ready=draft.request_ready,
                submitted_from_active_dataset=draft.submitted_from_active_dataset,
                progress_phase="queued",
                progress_percent_complete=0,
                progress_summary="Task accepted by rewrite in-memory scaffold.",
                progress_updated_at="2026-03-12 10:30:00",
            )
            session.add(row)
            session.commit()
            session.refresh(row)
            return _to_task_detail(row)

    def save_task_snapshot(self, task: TaskDetail) -> TaskDetail:
        with self._session_factory() as session:
            row = session.scalar(
                select(RewriteTaskRecord).where(RewriteTaskRecord.task_id == task.task_id)
            )
            if row is None:
                row = RewriteTaskRecord(task_id=task.task_id)
                session.add(row)

            row.kind = task.kind
            row.lane = task.lane
            row.execution_mode = task.execution_mode
            row.status = task.status
            row.submitted_at = task.submitted_at
            row.owner_user_id = task.owner_user_id
            row.owner_display_name = task.owner_display_name
            row.workspace_id = task.workspace_id
            row.workspace_slug = task.workspace_slug
            row.visibility_scope = task.visibility_scope
            row.dataset_id = task.dataset_id
            row.definition_id = task.definition_id
            row.summary = task.summary
            row.queue_backend = task.queue_backend
            row.worker_task_name = task.worker_task_name
            row.request_ready = task.request_ready
            row.submitted_from_active_dataset = task.submitted_from_active_dataset
            row.progress_phase = task.progress.phase
            row.progress_percent_complete = task.progress.percent_complete
            row.progress_summary = task.progress.summary
            row.progress_updated_at = task.progress.updated_at
            session.commit()
            session.refresh(row)
            return _to_task_detail(row)


def _to_task_detail(row: RewriteTaskRecord) -> TaskDetail:
    return TaskDetail(
        task_id=row.task_id,
        kind=cast(TaskKind, row.kind),
        lane=cast(TaskLane, row.lane),
        execution_mode=cast(TaskExecutionMode, row.execution_mode),
        status=cast(TaskStatus, row.status),
        submitted_at=row.submitted_at,
        owner_user_id=row.owner_user_id,
        owner_display_name=row.owner_display_name,
        workspace_id=row.workspace_id,
        workspace_slug=row.workspace_slug,
        visibility_scope=cast(TaskVisibilityScope, row.visibility_scope),
        dataset_id=row.dataset_id,
        definition_id=row.definition_id,
        summary=row.summary,
        queue_backend=cast(TaskQueueBackend, row.queue_backend),
        worker_task_name=cast(WorkerTaskName, row.worker_task_name),
        request_ready=row.request_ready,
        submitted_from_active_dataset=row.submitted_from_active_dataset,
        progress=TaskProgress(
            phase=cast(TaskStatus, row.progress_phase),
            percent_complete=row.progress_percent_complete,
            summary=row.progress_summary,
            updated_at=row.progress_updated_at,
        ),
        result_refs=_empty_result_refs(),
    )


def _empty_result_refs() -> TaskResultRefs:
    from sc_core.execution import TaskResultHandle

    return TaskResultRefs(
        result_handle=TaskResultHandle(),
        metadata_records=(),
        trace_payload=None,
        result_handles=(),
    )
