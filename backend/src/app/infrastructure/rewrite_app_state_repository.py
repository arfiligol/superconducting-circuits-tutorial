from dataclasses import replace

from src.app.domain.session import SessionState, SessionUser
from src.app.domain.tasks import (
    TaskCreateDraft,
    TaskDetail,
    TaskProgress,
    TaskResultRefs,
)


class InMemoryRewriteAppStateRepository:
    def __init__(self) -> None:
        self._session_state = _seed_session_state()
        self._tasks = {task.task_id: task for task in _seed_tasks()}
        self._next_task_id = max(self._tasks) + 1

    def get_session_state(self) -> SessionState:
        return self._session_state

    def set_active_dataset_id(self, dataset_id: str | None) -> SessionState:
        self._session_state = replace(self._session_state, active_dataset_id=dataset_id)
        return self._session_state

    def list_tasks(self) -> list[TaskDetail]:
        return list(self._tasks.values())

    def get_task(self, task_id: int) -> TaskDetail | None:
        return self._tasks.get(task_id)

    def create_task(self, draft: TaskCreateDraft) -> TaskDetail:
        task = TaskDetail(
            task_id=self._next_task_id,
            kind=draft.kind,
            lane=draft.lane,
            status="queued",
            submitted_at="2026-03-12 10:30:00",
            submitted_by=draft.submitted_by,
            dataset_id=draft.dataset_id,
            definition_id=draft.definition_id,
            summary=draft.summary,
            queue_backend="in_memory_scaffold",
            worker_task_name=draft.worker_task_name,
            submitted_from_active_dataset=draft.submitted_from_active_dataset,
            progress=TaskProgress(
                phase="queued",
                percent_complete=0,
                summary="Task accepted by rewrite in-memory scaffold.",
                updated_at="2026-03-12 10:30:00",
            ),
            result_refs=TaskResultRefs(trace_batch_id=None, analysis_run_id=None),
        )
        self._tasks[task.task_id] = task
        self._next_task_id += 1
        return task


def _seed_session_state() -> SessionState:
    return SessionState(
        session_id="rewrite-local-session",
        auth_state="authenticated",
        auth_mode="development_stub",
        scopes=("datasets:read", "datasets:write", "tasks:read", "tasks:submit"),
        user=SessionUser(
            user_id="researcher-01",
            display_name="Rewrite Local User",
            email="rewrite.local@example.com",
        ),
        active_dataset_id="fluxonium-2025-031",
    )


def _seed_tasks() -> tuple[TaskDetail, ...]:
    return (
        TaskDetail(
            task_id=301,
            kind="simulation",
            lane="simulation",
            status="running",
            submitted_at="2026-03-12 09:15:00",
            submitted_by="Rewrite Local User",
            dataset_id="fluxonium-2025-031",
            definition_id=18,
            summary="Fluxonium parameter sweep is running.",
            queue_backend="in_memory_scaffold",
            worker_task_name="simulation_run_task",
            submitted_from_active_dataset=True,
            progress=TaskProgress(
                phase="running",
                percent_complete=55,
                summary="simulation_run_task started in the simulation lane.",
                updated_at="2026-03-12 09:22:00",
            ),
            result_refs=TaskResultRefs(trace_batch_id=None, analysis_run_id=None),
        ),
        TaskDetail(
            task_id=302,
            kind="characterization",
            lane="characterization",
            status="queued",
            submitted_at="2026-03-12 08:40:00",
            submitted_by="Rewrite Local User",
            dataset_id="transmon-coupler-014",
            definition_id=None,
            summary="Coupler dataset characterization is queued.",
            queue_backend="in_memory_scaffold",
            worker_task_name="characterization_smoke_task",
            submitted_from_active_dataset=False,
            progress=TaskProgress(
                phase="queued",
                percent_complete=0,
                summary="Task accepted by rewrite in-memory scaffold.",
                updated_at="2026-03-12 08:40:00",
            ),
            result_refs=TaskResultRefs(trace_batch_id=None, analysis_run_id=None),
        ),
        TaskDetail(
            task_id=303,
            kind="post_processing",
            lane="simulation",
            status="completed",
            submitted_at="2026-03-11 19:05:00",
            submitted_by="Rewrite Local User",
            dataset_id="fluxonium-2025-031",
            definition_id=None,
            summary="Fluxonium fit bundle was post-processed.",
            queue_backend="in_memory_scaffold",
            worker_task_name="post_processing_run_task",
            submitted_from_active_dataset=True,
            progress=TaskProgress(
                phase="completed",
                percent_complete=100,
                summary="post_processing_run_task completed in the simulation lane.",
                updated_at="2026-03-11 19:18:00",
            ),
            result_refs=TaskResultRefs(trace_batch_id=88, analysis_run_id=None),
        ),
    )
