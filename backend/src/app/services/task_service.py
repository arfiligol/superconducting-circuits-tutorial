from __future__ import annotations

from collections.abc import Sequence
from dataclasses import replace
from datetime import datetime, timezone
from typing import Protocol

from sc_core.tasking import resolve_worker_task_route

from src.app.domain.audit import AuditRecord
from src.app.domain.datasets import DatasetDetail
from src.app.domain.session import SessionState
from src.app.domain.tasks import (
    TaskAllowedActions,
    TaskCreateDraft,
    TaskDetail,
    TaskEvent,
    TaskEventHistoryQuery,
    TaskHistoryView,
    TaskKind,
    TaskLifecycleUpdate,
    TaskListQuery,
    TaskQueueRow,
    TaskQueueView,
    TaskResultAvailability,
    TaskResultHandoff,
    TaskSubmissionDraft,
    WorkerLaneSummary,
    build_task_control_event,
    build_task_dispatch,
    build_task_retry_event,
    task_submission_source_for,
)
from src.app.services.service_errors import ServiceFieldError, service_error


class TaskRepository(Protocol):
    def list_tasks(self) -> Sequence[TaskDetail]: ...

    def get_task(self, task_id: int) -> TaskDetail | None: ...

    def get_task_history_view(self, task_id: int) -> TaskHistoryView | None: ...

    def list_task_events(self, task_id: int) -> Sequence[TaskEvent]: ...

    def create_task(self, draft: TaskCreateDraft) -> TaskDetail: ...

    def update_task_lifecycle(self, update: TaskLifecycleUpdate) -> TaskDetail | None: ...

    def merge_task_event_metadata(
        self,
        task_id: int,
        event_key: str,
        metadata: dict[str, object],
    ) -> None: ...

    def append_task_event(
        self,
        task_id: int,
        event: TaskEvent,
    ) -> None: ...


class TaskDatasetRepository(Protocol):
    def get_dataset(self, dataset_id: str) -> DatasetDetail | None: ...


class TaskCircuitDefinitionRepository(Protocol):
    def get_circuit_definition(self, definition_id: int) -> object | None: ...


class TaskSessionRepository(Protocol):
    def get_session_state(self) -> SessionState: ...


class TaskAuditRepository(Protocol):
    def append(self, record: AuditRecord) -> None: ...


class TaskService:
    def __init__(
        self,
        repository: TaskRepository,
        session_repository: TaskSessionRepository,
        dataset_repository: TaskDatasetRepository,
        circuit_definition_repository: TaskCircuitDefinitionRepository,
        audit_repository: TaskAuditRepository | None = None,
    ) -> None:
        self._repository = repository
        self._session_repository = session_repository
        self._dataset_repository = dataset_repository
        self._circuit_definition_repository = circuit_definition_repository
        self._audit_repository = audit_repository

    def list_tasks(self, query: TaskListQuery) -> list[TaskDetail]:
        tasks = [
            self._normalize_task(task)
            for task in self._repository.list_tasks()
            if self._matches_query(task, query)
        ]
        return _sort_tasks(tasks)[: query.limit]

    def get_queue_view(self, query: TaskListQuery) -> TaskQueueView:
        visible_tasks = [
            self._normalize_task(task)
            for task in self._repository.list_tasks()
            if self._matches_query(task, query)
        ]
        sorted_tasks = _sort_tasks(visible_tasks)
        rows = tuple(_build_queue_row(task) for task in sorted_tasks[: query.limit])
        return TaskQueueView(
            rows=rows,
            worker_summary=_build_worker_summary(
                visible_tasks=[
                    self._normalize_task(task)
                    for task in self._repository.list_tasks()
                    if self._is_visible(
                        task,
                        self._session_repository.get_session_state(),
                        scope="workspace",
                    )
                ]
            ),
            total_count=len(sorted_tasks),
            next_cursor=str(rows[-1].task_id) if len(sorted_tasks) > query.limit and len(rows) > 0 else None,
            prev_cursor=None,
            has_more=len(sorted_tasks) > query.limit,
        )

    def get_task(self, task_id: int) -> TaskDetail:
        history = self._load_visible_task_history(task_id)
        return replace(
            history.task,
            events=tuple(
                _select_task_events(
                    history.task.events,
                    TaskEventHistoryQuery(
                        order="asc",
                        limit=history.event_count,
                    ),
                )
            ),
        )

    def get_task_result_handoff(self, task_id: int) -> TaskResultHandoff:
        return _build_result_handoff(self.get_task(task_id))

    def get_task_allowed_actions(self, task_id: int) -> TaskAllowedActions:
        return _build_allowed_actions(self.get_task(task_id))

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

        owner_user_id = _session_user_id(session)
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
        detail = self.get_task(created_task.task_id)
        self._merge_submission_audit_metadata(detail)
        self._append_audit_record(
            action_kind="task.submitted",
            resource_id=str(detail.task_id),
            outcome="accepted",
            payload={
                "task_kind": detail.kind,
                "lane": detail.lane,
                "dataset_id": detail.dataset_id,
                "definition_id": detail.definition_id,
                "submission_source": detail.dispatch.submission_source if detail.dispatch else None,
            },
        )
        return self.get_task(created_task.task_id)

    def cancel_task(self, task_id: int) -> TaskDetail:
        task = self.get_task(task_id)
        allowed_actions = _build_allowed_actions(task)
        if not allowed_actions.cancel:
            raise service_error(
                409,
                code="task_not_cancellable",
                category="conflict",
                message="The task cannot be cancelled in its current state.",
            )
        event = build_task_control_event(
            task=task,
            control_state="cancellation_requested",
            occurred_at=_generated_at(),
            actor_user_id=_session_user_id(self._session_repository.get_session_state()),
        )
        self._repository.append_task_event(task_id, event)
        self._append_audit_record(
            action_kind="task.cancel_requested",
            resource_id=str(task_id),
            outcome="accepted",
            payload={
                "task_status": task.status,
                "lane": task.lane,
            },
        )
        return self.get_task(task_id)

    def terminate_task(self, task_id: int) -> TaskDetail:
        task = self.get_task(task_id)
        allowed_actions = _build_allowed_actions(task)
        if not allowed_actions.terminate:
            raise service_error(
                409,
                code="task_not_terminable",
                category="conflict",
                message="The task cannot be force terminated in its current state.",
            )
        event = build_task_control_event(
            task=task,
            control_state="termination_requested",
            occurred_at=_generated_at(),
            actor_user_id=_session_user_id(self._session_repository.get_session_state()),
        )
        self._repository.append_task_event(task_id, event)
        self._append_audit_record(
            action_kind="task.terminate_requested",
            resource_id=str(task_id),
            outcome="accepted",
            payload={
                "task_status": task.status,
                "lane": task.lane,
            },
        )
        return self.get_task(task_id)

    def retry_task(self, task_id: int) -> TaskDetail:
        source_task = self.get_task(task_id)
        allowed_actions = _build_allowed_actions(source_task)
        if not allowed_actions.retry:
            raise service_error(
                409,
                code="task_retry_denied",
                category="conflict",
                message="The task cannot be retried in its current state.",
            )

        created = self._repository.create_task(
            TaskCreateDraft(
                kind=source_task.kind,
                lane=source_task.lane,
                execution_mode=source_task.execution_mode,
                owner_user_id=source_task.owner_user_id,
                owner_display_name=source_task.owner_display_name,
                workspace_id=source_task.workspace_id,
                workspace_slug=source_task.workspace_slug,
                visibility_scope=source_task.visibility_scope,
                dataset_id=source_task.dataset_id,
                definition_id=source_task.definition_id,
                summary=f"Retry of task {source_task.task_id}: {source_task.summary}",
                worker_task_name=source_task.worker_task_name,
                request_ready=source_task.request_ready,
                submitted_from_active_dataset=source_task.submitted_from_active_dataset,
                submission_source=(
                    source_task.dispatch.submission_source
                    if source_task.dispatch is not None
                    else task_submission_source_for(
                        submitted_from_active_dataset=source_task.submitted_from_active_dataset,
                        dataset_id=source_task.dataset_id,
                    )
                ),
                retry_of_task_id=source_task.task_id,
            )
        )
        created_detail = self.get_task(created.task_id)
        retry_event = build_task_retry_event(
            source_task=source_task,
            replacement_task_id=created_detail.task_id,
            occurred_at=_generated_at(),
            actor_user_id=_session_user_id(self._session_repository.get_session_state()),
        )
        self._repository.append_task_event(source_task.task_id, retry_event)
        self._repository.append_task_event(
            created_detail.task_id,
            TaskEvent(
                event_key=f"task_retried:{retry_event.occurred_at}:source",
                event_type="task_retried",
                level="info",
                occurred_at=retry_event.occurred_at,
                message="Task was created as a retry of a previous terminal task.",
                metadata={
                    "retry_of_task_id": source_task.task_id,
                    "actor_user_id": _session_user_id(self._session_repository.get_session_state()),
                    "audit_action": "task.retried",
                },
            ),
        )
        self._merge_submission_audit_metadata(created_detail)
        self._append_audit_record(
            action_kind="task.retried",
            resource_id=str(created_detail.task_id),
            outcome="accepted",
            payload={
                "retry_of_task_id": source_task.task_id,
                "source_status": source_task.status,
                "lane": source_task.lane,
            },
        )
        return self.get_task(created_detail.task_id)

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
        history = self._load_visible_task_history(task_id)
        selected_events = tuple(_select_task_events(history.task.events, query))
        latest_event = selected_events[0] if query.order == "desc" and len(selected_events) > 0 else history.latest_event
        return TaskHistoryView(
            task=replace(history.task, events=selected_events),
            event_count=history.event_count,
            latest_event=latest_event,
        )

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

    def _load_visible_task_history(self, task_id: int) -> TaskHistoryView:
        history = self._repository.get_task_history_view(task_id)
        session = self._session_repository.get_session_state()
        if history is None or not self._is_visible(history.task, session, scope="workspace"):
            raise service_error(
                404,
                code="task_not_found",
                category="not_found",
                message=f"Task {task_id} was not found.",
            )
        normalized_task = self._normalize_task(history.task)
        latest_event_candidates = _select_task_events(
            normalized_task.events,
            TaskEventHistoryQuery(order="desc", limit=1),
        )
        return TaskHistoryView(
            task=normalized_task,
            event_count=len(normalized_task.events),
            latest_event=latest_event_candidates[0] if len(latest_event_candidates) > 0 else None,
        )

    def _matches_query(self, task: TaskDetail, query: TaskListQuery) -> bool:
        session = self._session_repository.get_session_state()
        if not self._is_visible(task, session, scope=query.scope):
            return False
        if query.status is not None and task.status != query.status:
            return False
        if query.lane is not None and task.lane != query.lane:
            return False
        if query.dataset_id is not None and task.dataset_id != query.dataset_id:
            return False
        if query.search_query is None:
            return True
        needle = query.search_query.casefold()
        return (
            needle in task.summary.casefold()
            or needle in task.owner_display_name.casefold()
            or needle in str(task.task_id)
        )

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
                    TaskEventHistoryQuery(order="asc", limit=max(len(task.events), 1)),
                )
            ),
        )

    def _merge_submission_audit_metadata(self, task: TaskDetail) -> None:
        if len(task.events) == 0:
            return
        self._repository.merge_task_event_metadata(
            task.task_id,
            task.events[0].event_key,
            {"audit_action": "task.submitted"},
        )

    def _append_audit_record(
        self,
        *,
        action_kind: str,
        resource_id: str,
        outcome: str,
        payload: dict[str, object],
    ) -> None:
        if self._audit_repository is None:
            return
        session = self._session_repository.get_session_state()
        occurred_at = _generated_at()
        actor_display_name = session.user.display_name if session.user is not None else "anonymous"
        correlation_id = f"corr:{action_kind}:{resource_id}"
        audit_suffix = occurred_at.replace(":", "-").replace("+", "z")
        self._audit_repository.append(
            AuditRecord(
                audit_id=f"audit:{action_kind}:{resource_id}:{audit_suffix}",
                occurred_at=occurred_at,
                actor_user_id=_session_user_id(session),
                actor_display_name=actor_display_name,
                session_id=session.session_id,
                correlation_id=correlation_id,
                workspace_id=session.workspace_id,
                action_kind=action_kind,
                resource_kind="task",
                resource_id=resource_id,
                outcome=outcome,
                payload=payload,
                debug_ref=f"debug:{action_kind}:{resource_id}",
            )
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


def _sort_tasks(tasks: Sequence[TaskDetail]) -> list[TaskDetail]:
    return sorted(
        tasks,
        key=lambda task: (_task_priority(task), task.progress.updated_at, task.task_id),
        reverse=True,
    )


def _task_priority(task: TaskDetail) -> int:
    if task.status in {"running", "queued"}:
        return 2
    if task.control_state != "none":
        return 1
    return 0


def _build_queue_row(task: TaskDetail) -> TaskQueueRow:
    return TaskQueueRow(
        task_id=task.task_id,
        summary=task.summary,
        status=task.status,
        control_state=task.control_state,
        lane=task.lane,
        task_kind=task.kind,
        owner_display_name=task.owner_display_name,
        visibility_scope=task.visibility_scope,
        updated_at=task.progress.updated_at,
        result_availability=_result_availability_for(task),
        allowed_actions=_build_allowed_actions(task),
    )


def _build_allowed_actions(task: TaskDetail) -> TaskAllowedActions:
    if task.status in {"completed", "failed"}:
        return TaskAllowedActions(
            attach=True,
            cancel=False,
            terminate=False,
            retry=True,
            rejection_reason="task_already_terminal",
        )
    if task.control_state == "termination_requested":
        return TaskAllowedActions(
            attach=True,
            cancel=False,
            terminate=False,
            retry=False,
            rejection_reason="termination_requested",
        )
    if task.control_state == "cancellation_requested":
        return TaskAllowedActions(
            attach=True,
            cancel=False,
            terminate=True,
            retry=False,
            rejection_reason="cancellation_requested",
        )
    if task.status == "running":
        return TaskAllowedActions(
            attach=True,
            cancel=True,
            terminate=True,
            retry=False,
        )
    return TaskAllowedActions(
        attach=True,
        cancel=True,
        terminate=False,
        retry=False,
    )


def _build_result_handoff(task: TaskDetail) -> TaskResultHandoff:
    return TaskResultHandoff(
        availability=_result_availability_for(task),
        primary_result_handle_id=(
            task.result_refs.result_handles[0].handle_id if len(task.result_refs.result_handles) > 0 else None
        ),
        result_handle_count=len(task.result_refs.result_handles),
        trace_payload_available=task.result_refs.trace_payload is not None,
    )


def _result_availability_for(task: TaskDetail) -> TaskResultAvailability:
    if task.result_refs.trace_payload is not None:
        return "ready"
    if any(handle.status == "materialized" for handle in task.result_refs.result_handles):
        return "ready"
    if task.status in {"completed", "failed"}:
        return "none"
    return "pending"


def _build_worker_summary(
    *,
    visible_tasks: Sequence[TaskDetail],
) -> tuple[WorkerLaneSummary, ...]:
    summaries: list[WorkerLaneSummary] = []
    for lane in ("simulation", "characterization"):
        lane_tasks = [task for task in visible_tasks if task.lane == lane]
        busy_processors = sum(1 for task in lane_tasks if task.status == "running")
        degraded_processors = sum(1 for task in lane_tasks if task.control_state != "none")
        summaries.append(
            WorkerLaneSummary(
                lane=lane,
                healthy_processors=max(1 - min(degraded_processors, 1), 0),
                busy_processors=busy_processors,
                degraded_processors=degraded_processors,
                draining_processors=0,
                offline_processors=0,
            )
        )
    return tuple(summaries)


def _generated_at() -> str:
    return datetime.now(timezone.utc).isoformat()
