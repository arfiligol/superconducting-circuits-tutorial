"""Stable rewrite contract facade for CLI consumption."""

from collections.abc import Callable

from fastapi import HTTPException
from src.app.api.schemas.circuit_definitions import (
    CircuitDefinitionDetailResponse,
    CircuitDefinitionValidationSummaryResponse,
    ValidationNoticeResponse,
)
from src.app.api.schemas.datasets import DatasetSummaryResponse
from src.app.api.schemas.session import (
    ActiveDatasetResponse,
    SessionAuthResponse,
    SessionResponse,
    SessionUserResponse,
    WorkspaceContextResponse,
)
from src.app.api.schemas.tasks import (
    TaskDetailResponse,
    TaskProgressResponse,
    TaskResultRefsResponse,
    TaskSummaryResponse,
)
from src.app.domain.circuit_definitions import CircuitDefinitionDetail
from src.app.domain.datasets import (
    DatasetListQuery,
    DatasetSortBy,
    DatasetStatus,
    DatasetSummary,
    SortOrder,
)
from src.app.domain.session import AppSession
from src.app.domain.tasks import (
    TaskDetail,
    TaskLane,
    TaskListQuery,
    TaskStatus,
    TaskVisibilityScope,
)
from src.app.infrastructure.runtime import (
    get_circuit_definition_service,
    get_dataset_service,
    get_session_service,
    get_task_service,
)
from src.app.infrastructure.runtime import (
    reset_runtime_state as _reset_runtime_state,
)
from src.app.services.service_errors import ServiceError

from sc_backend.errors import backend_contract_error

reset_runtime_state = _reset_runtime_state


def get_session() -> SessionResponse:
    return _build_session_response(_run_backend_call(get_session_service().get_session))


def list_datasets(
    *,
    family: str | None = None,
    status: DatasetStatus | None = None,
    sort_by: DatasetSortBy = "updated_at",
    sort_order: SortOrder = "desc",
) -> list[DatasetSummaryResponse]:
    return [
        _build_dataset_summary_response(summary)
        for summary in _run_backend_call(
            lambda: get_dataset_service().list_datasets(
                DatasetListQuery(
                    family=family,
                    status=status,
                    sort_by=sort_by,
                    sort_order=sort_order,
                )
            )
        )
    ]


def list_tasks(
    *,
    status: TaskStatus | None = None,
    lane: TaskLane | None = None,
    scope: TaskVisibilityScope = "workspace",
    dataset_id: str | None = None,
    limit: int = 20,
) -> list[TaskSummaryResponse]:
    return [
        _build_task_summary_response(task)
        for task in _run_backend_call(
            lambda: get_task_service().list_tasks(
                TaskListQuery(
                    status=status,
                    lane=lane,
                    scope=scope,
                    dataset_id=dataset_id,
                    limit=limit,
                )
            )
        )
    ]


def get_task(task_id: int) -> TaskDetailResponse:
    return _build_task_detail_response(
        _run_backend_call(lambda: get_task_service().get_task(task_id))
    )


def get_circuit_definition(definition_id: int) -> CircuitDefinitionDetailResponse:
    return _build_circuit_definition_detail_response(
        _run_backend_call(
            lambda: get_circuit_definition_service().get_circuit_definition(definition_id)
        )
    )


def _run_backend_call[T](operation: Callable[[], T]) -> T:
    try:
        return operation()
    except (HTTPException, ServiceError) as exc:
        raise backend_contract_error(exc) from exc


def _build_session_response(session: AppSession) -> SessionResponse:
    return SessionResponse(
        session_id=session.session_id,
        auth=SessionAuthResponse(
            state=session.auth_state,
            mode=session.auth_mode,
            scopes=list(session.scopes),
            can_submit_tasks=session.can_submit_tasks,
            can_manage_datasets=session.can_manage_datasets,
        ),
        identity=(
            SessionUserResponse(
                user_id=session.identity.user_id,
                display_name=session.identity.display_name,
                email=session.identity.email,
            )
            if session.identity is not None
            else None
        ),
        workspace=WorkspaceContextResponse(
            workspace_id=session.workspace.workspace_id,
            slug=session.workspace.slug,
            display_name=session.workspace.display_name,
            role=session.workspace.role,
            default_task_scope=session.workspace.default_task_scope,
            active_dataset=(
                ActiveDatasetResponse(
                    dataset_id=session.workspace.active_dataset.dataset_id,
                    name=session.workspace.active_dataset.name,
                    family=session.workspace.active_dataset.family,
                    status=session.workspace.active_dataset.status,
                    owner=session.workspace.active_dataset.owner,
                    access_scope=session.workspace.active_dataset.access_scope,
                )
                if session.workspace.active_dataset is not None
                else None
            ),
        ),
    )


def _build_dataset_summary_response(summary: DatasetSummary) -> DatasetSummaryResponse:
    return DatasetSummaryResponse.model_validate(summary.__dict__)


def _build_task_summary_response(task: TaskDetail) -> TaskSummaryResponse:
    return TaskSummaryResponse(
        task_id=task.task_id,
        kind=task.kind,
        lane=task.lane,
        execution_mode=task.execution_mode,
        status=task.status,
        submitted_at=task.submitted_at,
        owner_user_id=task.owner_user_id,
        owner_display_name=task.owner_display_name,
        workspace_id=task.workspace_id,
        workspace_slug=task.workspace_slug,
        visibility_scope=task.visibility_scope,
        dataset_id=task.dataset_id,
        definition_id=task.definition_id,
        summary=task.summary,
    )


def _build_task_detail_response(task: TaskDetail) -> TaskDetailResponse:
    return TaskDetailResponse(
        task_id=task.task_id,
        kind=task.kind,
        lane=task.lane,
        execution_mode=task.execution_mode,
        status=task.status,
        submitted_at=task.submitted_at,
        owner_user_id=task.owner_user_id,
        owner_display_name=task.owner_display_name,
        workspace_id=task.workspace_id,
        workspace_slug=task.workspace_slug,
        visibility_scope=task.visibility_scope,
        dataset_id=task.dataset_id,
        definition_id=task.definition_id,
        summary=task.summary,
        queue_backend=task.queue_backend,
        worker_task_name=task.worker_task_name,
        request_ready=task.request_ready,
        submitted_from_active_dataset=task.submitted_from_active_dataset,
        progress=TaskProgressResponse(
            phase=task.progress.phase,
            percent_complete=task.progress.percent_complete,
            summary=task.progress.summary,
            updated_at=task.progress.updated_at,
        ),
        result_refs=TaskResultRefsResponse(
            trace_batch_id=task.result_refs.trace_batch_id,
            analysis_run_id=task.result_refs.analysis_run_id,
        ),
    )


def _build_circuit_definition_detail_response(
    detail: CircuitDefinitionDetail,
) -> CircuitDefinitionDetailResponse:
    warning_count = sum(1 for notice in detail.validation_notices if notice.level == "warning")
    return CircuitDefinitionDetailResponse(
        definition_id=detail.definition_id,
        name=detail.name,
        created_at=detail.created_at,
        element_count=detail.element_count,
        validation_status="warning" if warning_count else "ok",
        preview_artifact_count=len(detail.preview_artifacts),
        source_text=detail.source_text,
        normalized_output=detail.normalized_output,
        validation_notices=[
            ValidationNoticeResponse(level=notice.level, message=notice.message)
            for notice in detail.validation_notices
        ],
        validation_summary=CircuitDefinitionValidationSummaryResponse(
            status="warning" if warning_count else "ok",
            notice_count=len(detail.validation_notices),
            warning_count=warning_count,
        ),
        preview_artifacts=list(detail.preview_artifacts),
    )
