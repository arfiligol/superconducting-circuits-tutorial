from collections.abc import Sequence
from typing import Protocol

from sc_core.tasking import resolve_worker_task_route
from src.app.domain.circuit_definitions import CircuitDefinitionDetail
from src.app.domain.datasets import DatasetDetail
from src.app.domain.session import SessionState
from src.app.domain.tasks import (
    TaskCreateDraft,
    TaskDetail,
    TaskKind,
    TaskListQuery,
    TaskSubmissionDraft,
)
from src.app.services.service_errors import api_error


class TaskRepository(Protocol):
    def list_tasks(self) -> Sequence[TaskDetail]: ...

    def get_task(self, task_id: int) -> TaskDetail | None: ...

    def create_task(self, draft: TaskCreateDraft) -> TaskDetail: ...


class TaskDatasetRepository(Protocol):
    def get_dataset(self, dataset_id: str) -> DatasetDetail | None: ...


class TaskCircuitDefinitionRepository(Protocol):
    def get_circuit_definition(self, definition_id: int) -> CircuitDefinitionDetail | None: ...


class TaskSessionRepository(Protocol):
    def get_session_state(self) -> SessionState: ...


class TaskService:
    def __init__(
        self,
        repository: TaskRepository,
        session_repository: TaskSessionRepository,
        dataset_repository: TaskDatasetRepository,
        circuit_definition_repository: TaskCircuitDefinitionRepository,
    ) -> None:
        self._repository = repository
        self._session_repository = session_repository
        self._dataset_repository = dataset_repository
        self._circuit_definition_repository = circuit_definition_repository

    def list_tasks(self, query: TaskListQuery) -> list[TaskDetail]:
        tasks = [task for task in self._repository.list_tasks() if self._matches_query(task, query)]
        return sorted(tasks, key=lambda task: task.submitted_at, reverse=True)[: query.limit]

    def get_task(self, task_id: int) -> TaskDetail:
        detail = self._repository.get_task(task_id)
        session = self._session_repository.get_session_state()
        if detail is None or not self._is_visible(detail, session, scope="workspace"):
            raise api_error(
                404,
                code="task_not_found",
                category="not_found",
                message=f"Task {task_id} was not found.",
            )
        return detail

    def submit_task(self, draft: TaskSubmissionDraft) -> TaskDetail:
        session = self._session_repository.get_session_state()
        resolved_dataset_id = draft.dataset_id or session.active_dataset_id
        submitted_from_active_dataset = draft.dataset_id is None and resolved_dataset_id is not None

        if draft.kind == "simulation" and draft.definition_id is None:
            raise api_error(
                422,
                code="simulation_definition_required",
                category="validation",
                message="Simulation tasks require definition_id.",
            )

        if draft.kind in {"post_processing", "characterization"} and resolved_dataset_id is None:
            raise api_error(
                422,
                code="dataset_context_required",
                category="validation",
                message=f"{draft.kind} tasks require dataset_id or an active dataset.",
            )

        if (
            resolved_dataset_id is not None
            and self._dataset_repository.get_dataset(resolved_dataset_id) is None
        ):
            raise api_error(
                404,
                code="dataset_not_found",
                category="not_found",
                message=f"Dataset {resolved_dataset_id} was not found.",
            )

        if (
            draft.definition_id is not None
            and self._circuit_definition_repository.get_circuit_definition(
                draft.definition_id
            )
            is None
        ):
            raise api_error(
                404,
                code="circuit_definition_not_found",
                category="not_found",
                message=f"Circuit definition {draft.definition_id} was not found.",
            )

        owner_user_id = session.user.user_id if session.user is not None else "anonymous"
        owner_display_name = session.user.display_name if session.user is not None else "anonymous"
        worker_route = resolve_worker_task_route(
            draft.kind,
            request_is_valid=True,
            has_trace_batch_id=False,
        )
        return self._repository.create_task(
            TaskCreateDraft(
                kind=draft.kind,
                lane=worker_route.lane,
                execution_mode=worker_route.execution_mode,
                owner_user_id=owner_user_id,
                owner_display_name=owner_display_name,
                workspace_id=session.workspace_id,
                workspace_slug=session.workspace_slug,
                visibility_scope="workspace",
                dataset_id=resolved_dataset_id,
                definition_id=draft.definition_id,
                summary=draft.summary or _default_task_summary(draft.kind, resolved_dataset_id),
                worker_task_name=worker_route.worker_task_name,
                request_ready=worker_route.request_ready,
                submitted_from_active_dataset=submitted_from_active_dataset,
            )
        )

    def _matches_query(self, task: TaskDetail, query: TaskListQuery) -> bool:
        session = self._session_repository.get_session_state()
        if not self._is_visible(task, session, scope=query.scope):
            return False
        if query.status is not None and task.status != query.status:
            return False
        if query.lane is not None and task.lane != query.lane:
            return False
        return query.dataset_id is None or task.dataset_id == query.dataset_id

    def _is_visible(
        self,
        task: TaskDetail,
        session: SessionState,
        *,
        scope: str,
    ) -> bool:
        if task.workspace_id != session.workspace_id:
            return False
        if task.visibility_scope == "owned" and task.owner_user_id != _session_user_id(session):
            return False
        if scope == "owned":
            return task.owner_user_id == _session_user_id(session)
        return True


def _default_task_summary(task_kind: TaskKind, dataset_id: str | None) -> str:
    if dataset_id is None:
        return f"{task_kind.replace('_', ' ')} task accepted by rewrite scaffold."
    return f"{task_kind.replace('_', ' ')} task accepted for dataset {dataset_id}."


def _session_user_id(session: SessionState) -> str:
    if session.user is None:
        return "anonymous"
    return session.user.user_id
