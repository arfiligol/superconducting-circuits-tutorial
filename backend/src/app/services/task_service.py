from collections.abc import Sequence
from typing import Protocol

from fastapi import HTTPException, status
from src.app.domain.circuit_definitions import CircuitDefinitionDetail
from src.app.domain.datasets import DatasetDetail
from src.app.domain.session import SessionState
from src.app.domain.tasks import (
    TaskCreateDraft,
    TaskDetail,
    TaskKind,
    TaskLane,
    TaskListQuery,
    TaskSubmissionDraft,
)


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
        if detail is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task {task_id} was not found.",
            )
        return detail

    def submit_task(self, draft: TaskSubmissionDraft) -> TaskDetail:
        session = self._session_repository.get_session_state()
        resolved_dataset_id = draft.dataset_id or session.active_dataset_id
        submitted_from_active_dataset = draft.dataset_id is None and resolved_dataset_id is not None

        if draft.kind == "simulation" and draft.definition_id is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail="Simulation tasks require definition_id.",
            )

        if draft.kind in {"post_processing", "characterization"} and resolved_dataset_id is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail=f"{draft.kind} tasks require dataset_id or an active dataset.",
            )

        if (
            resolved_dataset_id is not None
            and self._dataset_repository.get_dataset(resolved_dataset_id) is None
        ):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Dataset {resolved_dataset_id} was not found.",
            )

        if (
            draft.definition_id is not None
            and self._circuit_definition_repository.get_circuit_definition(
                draft.definition_id
            )
            is None
        ):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Circuit definition {draft.definition_id} was not found.",
            )

        submitted_by = session.user.display_name if session.user is not None else "anonymous"
        return self._repository.create_task(
            TaskCreateDraft(
                kind=draft.kind,
                lane=_lane_for_task_kind(draft.kind),
                submitted_by=submitted_by,
                dataset_id=resolved_dataset_id,
                definition_id=draft.definition_id,
                summary=draft.summary or _default_task_summary(draft.kind, resolved_dataset_id),
                worker_task_name=_worker_task_name_for(draft.kind),
                submitted_from_active_dataset=submitted_from_active_dataset,
            )
        )

    def _matches_query(self, task: TaskDetail, query: TaskListQuery) -> bool:
        if query.status is not None and task.status != query.status:
            return False
        if query.lane is not None and task.lane != query.lane:
            return False
        return query.dataset_id is None or task.dataset_id == query.dataset_id


def _lane_for_task_kind(task_kind: TaskKind) -> TaskLane:
    if task_kind == "characterization":
        return "characterization"
    return "simulation"


def _worker_task_name_for(task_kind: TaskKind) -> str:
    if task_kind == "simulation":
        return "simulation_smoke_task"
    if task_kind == "post_processing":
        return "post_processing_smoke_task"
    return "characterization_smoke_task"


def _default_task_summary(task_kind: TaskKind, dataset_id: str | None) -> str:
    if dataset_id is None:
        return f"{task_kind.replace('_', ' ')} task accepted by rewrite scaffold."
    return f"{task_kind.replace('_', ' ')} task accepted for dataset {dataset_id}."
