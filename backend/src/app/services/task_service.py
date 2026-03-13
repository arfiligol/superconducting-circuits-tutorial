from collections.abc import Sequence
from dataclasses import replace
from typing import Protocol

from sc_core.tasking import resolve_worker_task_route

from src.app.domain.circuit_definitions import CircuitDefinitionDetail
from src.app.domain.datasets import DatasetDetail
from src.app.domain.session import SessionState
from src.app.domain.tasks import (
    TaskCreateDraft,
    TaskDetail,
    TaskEvent,
    TaskEventHistoryQuery,
    TaskHistoryView,
    TaskKind,
    TaskLifecycleUpdate,
    TaskListQuery,
    TaskSubmissionDraft,
    build_task_dispatch,
    task_submission_source_for,
)
from src.app.services.service_errors import ServiceFieldError, service_error


class TaskRepository(Protocol):
    def list_tasks(self) -> Sequence[TaskDetail]: ...

    def get_task(self, task_id: int) -> TaskDetail | None: ...

    def list_task_events(self, task_id: int) -> Sequence[TaskEvent]: ...

    def create_task(self, draft: TaskCreateDraft) -> TaskDetail: ...

    def update_task_lifecycle(self, update: TaskLifecycleUpdate) -> TaskDetail | None: ...


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
        tasks = [
            self._normalize_task(task)
            for task in self._repository.list_tasks()
            if self._matches_query(task, query)
        ]
        return sorted(tasks, key=lambda task: task.submitted_at, reverse=True)[: query.limit]

    def get_task(self, task_id: int) -> TaskDetail:
        detail = self._load_visible_task(task_id)
        persisted_events = tuple(self._repository.list_task_events(task_id))
        normalized_task = self._normalize_task(detail)
        return replace(
            normalized_task,
            events=tuple(
                _select_task_events(
                    persisted_events,
                    TaskEventHistoryQuery(
                        order="asc",
                        limit=len(persisted_events),
                    ),
                )
            ),
        )

    def submit_task(self, draft: TaskSubmissionDraft) -> TaskDetail:
        session = self._session_repository.get_session_state()
        resolved_dataset_id = draft.dataset_id or session.active_dataset_id
        submitted_from_active_dataset = draft.dataset_id is None and resolved_dataset_id is not None

        if draft.kind == "simulation" and draft.definition_id is None:
            raise service_error(
                422,
                code="simulation_definition_required",
                category="validation",
                message="Simulation tasks require definition_id.",
            )

        if draft.kind in {"post_processing", "characterization"} and resolved_dataset_id is None:
            raise service_error(
                422,
                code="dataset_context_required",
                category="validation",
                message=f"{draft.kind} tasks require dataset_id or an active dataset.",
            )

        if (
            resolved_dataset_id is not None
            and self._dataset_repository.get_dataset(resolved_dataset_id) is None
        ):
            raise service_error(
                404,
                code="dataset_not_found",
                category="not_found",
                message=f"Dataset {resolved_dataset_id} was not found.",
            )

        if (
            draft.definition_id is not None
            and self._circuit_definition_repository.get_circuit_definition(draft.definition_id)
            is None
        ):
            raise service_error(
                404,
                code="circuit_definition_not_found",
                category="not_found",
                message=f"Circuit definition {draft.definition_id} was not found.",
            )

        owner_user_id = session.user.user_id if session.user is not None else "anonymous"
        owner_display_name = session.user.display_name if session.user is not None else "anonymous"
        submission_source = task_submission_source_for(
            submitted_from_active_dataset=submitted_from_active_dataset,
            dataset_id=resolved_dataset_id,
        )
        worker_route = resolve_worker_task_route(
            draft.kind,
            request_is_valid=True,
            has_trace_batch_id=False,
        )
        created_task = self._repository.create_task(
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
                submission_source=submission_source,
            )
        )
        return self.get_task(created_task.task_id)

    def list_task_events(
        self,
        task_id: int,
        query: TaskEventHistoryQuery,
    ) -> list[TaskEvent]:
        return list(self.get_task_history(task_id, query).task.events)

    def get_task_history(
        self,
        task_id: int,
        query: TaskEventHistoryQuery,
    ) -> TaskHistoryView:
        detail = self._load_visible_task(task_id)
        normalized_task = self._normalize_task(detail)
        persisted_events = tuple(self._repository.list_task_events(task_id))
        selected_events = tuple(_select_task_events(persisted_events, query))
        latest_event_candidates = _select_task_events(
            persisted_events,
            TaskEventHistoryQuery(order="desc", limit=1),
        )
        return TaskHistoryView(
            task=replace(normalized_task, events=selected_events),
            event_count=len(persisted_events),
            latest_event=latest_event_candidates[0] if len(latest_event_candidates) > 0 else None,
        )

    def _load_visible_task(self, task_id: int) -> TaskDetail:
        detail = self._repository.get_task(task_id)
        session = self._session_repository.get_session_state()
        if detail is None or not self._is_visible(detail, session, scope="workspace"):
            raise service_error(
                404,
                code="task_not_found",
                category="not_found",
                message=f"Task {task_id} was not found.",
            )
        return detail

    def update_task_lifecycle(self, update: TaskLifecycleUpdate) -> TaskDetail:
        detail = self._repository.get_task(update.task_id)
        if detail is None:
            raise service_error(
                404,
                code="task_not_found",
                category="not_found",
                message=f"Task {update.task_id} was not found.",
            )

        field_errors = _validate_task_lifecycle_update(update)
        if len(field_errors) > 0:
            raise service_error(
                422,
                code="task_lifecycle_update_invalid",
                category="validation",
                message="Task lifecycle update is invalid.",
                field_errors=field_errors,
            )

        enriched_update = replace(
            update,
            dispatch=build_task_dispatch(
                task_id=detail.task_id,
                worker_task_name=detail.worker_task_name,
                task_status=update.status,
                submitted_from_active_dataset=detail.submitted_from_active_dataset,
                dataset_id=detail.dataset_id,
                accepted_at=detail.submitted_at,
                last_updated_at=update.progress_updated_at,
                current_dispatch=detail.dispatch,
            ),
        )
        updated_task = self._repository.update_task_lifecycle(enriched_update)
        if updated_task is None:
            raise service_error(
                404,
                code="task_not_found",
                category="not_found",
                message=f"Task {update.task_id} was not found.",
            )
        return self.get_task(updated_task.task_id)

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

    def _normalize_task(self, task: TaskDetail) -> TaskDetail:
        return replace(
            task,
            dispatch=build_task_dispatch(
                task_id=task.task_id,
                worker_task_name=task.worker_task_name,
                task_status=task.status,
                submitted_from_active_dataset=task.submitted_from_active_dataset,
                dataset_id=task.dataset_id,
                accepted_at=task.submitted_at,
                last_updated_at=task.progress.updated_at,
                current_dispatch=task.dispatch,
            ),
            events=tuple(
                _select_task_events(
                    task.events,
                    TaskEventHistoryQuery(
                        order="asc",
                        limit=max(len(task.events), 1),
                    ),
                )
            ),
        )


def _default_task_summary(task_kind: TaskKind, dataset_id: str | None) -> str:
    if dataset_id is None:
        return f"{task_kind.replace('_', ' ')} task accepted by rewrite scaffold."
    return f"{task_kind.replace('_', ' ')} task accepted for dataset {dataset_id}."


def _session_user_id(session: SessionState) -> str:
    if session.user is None:
        return "anonymous"
    return session.user.user_id


def _validate_task_lifecycle_update(
    update: TaskLifecycleUpdate,
) -> tuple[ServiceFieldError, ...]:
    field_errors: list[ServiceFieldError] = []
    if not 0 <= update.progress_percent_complete <= 100:
        field_errors.append(
            ServiceFieldError(
                field="progress_percent_complete",
                message="progress_percent_complete must be between 0 and 100.",
            )
        )
    if update.status == "queued" and update.progress_percent_complete != 0:
        field_errors.append(
            ServiceFieldError(
                field="progress_percent_complete",
                message="Queued tasks must report 0 percent_complete.",
            )
        )
    if update.status == "running" and update.progress_percent_complete == 100:
        field_errors.append(
            ServiceFieldError(
                field="progress_percent_complete",
                message="Running tasks cannot report 100 percent_complete.",
            )
        )
    if update.status == "completed" and update.progress_percent_complete != 100:
        field_errors.append(
            ServiceFieldError(
                field="progress_percent_complete",
                message="Completed tasks must report 100 percent_complete.",
            )
        )
    if len(update.progress_summary.strip()) == 0:
        field_errors.append(
            ServiceFieldError(
                field="progress_summary",
                message="progress_summary must not be empty.",
            )
        )
    if len(update.progress_updated_at.strip()) == 0:
        field_errors.append(
            ServiceFieldError(
                field="progress_updated_at",
                message="progress_updated_at must not be empty.",
            )
        )
    return tuple(field_errors)


def _select_task_events(
    events: Sequence[TaskEvent],
    query: TaskEventHistoryQuery,
) -> list[TaskEvent]:
    filtered = [
        _redact_task_event(event)
        for event in events
        if query.event_type is None or event.event_type == query.event_type
    ]
    filtered.sort(
        key=lambda event: (event.occurred_at, event.event_key),
        reverse=query.order == "desc",
    )
    return filtered[: query.limit]


def _redact_task_event(event: TaskEvent) -> TaskEvent:
    safe_metadata = {
        key: value
        for key, value in event.metadata.items()
        if not _is_sensitive_event_field(key)
    }
    return replace(event, metadata=safe_metadata)


def _is_sensitive_event_field(field_name: str) -> bool:
    sensitive_tokens = (
        "secret",
        "token",
        "password",
        "credential",
        "payload_body",
        "request_body",
        "connection_string",
        "store_uri",
    )
    normalized = field_name.lower()
    return any(token in normalized for token in sensitive_tokens)
