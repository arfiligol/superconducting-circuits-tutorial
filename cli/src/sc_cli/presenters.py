"""Output formatting helpers for the CLI adapter layer."""

from collections.abc import Iterable
from pathlib import Path

from sc_backend import (
    ApiErrorBodyResponse,
    CircuitDefinitionDetailResponse,
    DatasetSummaryResponse,
    SessionResponse,
    TaskDetailResponse,
    TaskSummaryResponse,
)
from sc_core import CircuitDefinitionInspection


def render_preview_artifacts(artifacts: tuple[str, ...]) -> str:
    lines = ["sc_core preview artifacts:"]
    lines.extend(f"- {artifact}" for artifact in artifacts)
    return "\n".join(lines)


def render_circuit_definition_inspection(
    source_file: Path, inspection: CircuitDefinitionInspection
) -> str:
    lines = [
        f"source_file: {source_file}",
        f"circuit_name: {inspection.circuit_name}",
        f"family: {inspection.family}",
        f"element_count: {inspection.element_count}",
        "normalized_output:",
        inspection.normalized_output,
        "validation_notices:",
    ]
    lines.extend(f"- [{notice.level}] {notice.message}" for notice in inspection.validation_notices)
    return "\n".join(lines)


def render_session(session: SessionResponse) -> str:
    lines = [
        f"session_id: {session.session_id}",
        f"auth_state: {session.auth.state}",
        f"auth_mode: {session.auth.mode}",
        f"scopes: {', '.join(session.auth.scopes) if session.auth.scopes else '(none)'}",
        f"can_submit_tasks: {_render_bool(session.auth.can_submit_tasks)}",
        f"can_manage_datasets: {_render_bool(session.auth.can_manage_datasets)}",
        f"workspace_id: {session.workspace.workspace_id}",
        f"workspace_slug: {session.workspace.slug}",
        f"workspace_display_name: {session.workspace.display_name}",
        f"workspace_role: {session.workspace.role}",
        f"default_task_scope: {session.workspace.default_task_scope}",
    ]
    if session.identity is None:
        lines.append("identity: none")
    else:
        lines.extend(
            [
                f"identity_user_id: {session.identity.user_id}",
                f"identity_display_name: {session.identity.display_name}",
                f"identity_email: {session.identity.email or '-'}",
            ]
        )
    if session.workspace.active_dataset is None:
        lines.append("active_dataset: none")
    else:
        lines.extend(
            [
                f"active_dataset_id: {session.workspace.active_dataset.dataset_id}",
                f"active_dataset_name: {session.workspace.active_dataset.name}",
                f"active_dataset_family: {session.workspace.active_dataset.family}",
                f"active_dataset_status: {session.workspace.active_dataset.status}",
                f"active_dataset_owner: {session.workspace.active_dataset.owner}",
                f"active_dataset_access_scope: {session.workspace.active_dataset.access_scope}",
            ]
        )
    return "\n".join(lines)


def render_dataset_summaries(datasets: list[DatasetSummaryResponse]) -> str:
    lines = [f"datasets: {len(datasets)}"]
    lines.extend(
        _render_list_line(
            dataset.dataset_id,
            (
                dataset.name,
                f"family={dataset.family}",
                f"status={dataset.status}",
                f"samples={dataset.samples}",
                f"updated_at={dataset.updated_at}",
            ),
        )
        for dataset in datasets
    )
    return "\n".join(lines)


def render_task_summaries(tasks: list[TaskSummaryResponse]) -> str:
    lines = [f"tasks: {len(tasks)}"]
    lines.extend(
        _render_list_line(
            f"#{task.task_id}",
            (
                f"kind={task.kind}",
                f"lane={task.lane}",
                f"mode={task.execution_mode}",
                f"status={task.status}",
                f"scope={task.visibility_scope}",
                f"dataset={task.dataset_id or '-'}",
                f"definition={task.definition_id if task.definition_id is not None else '-'}",
                f"summary={task.summary}",
            ),
        )
        for task in tasks
    )
    return "\n".join(lines)


def render_task_detail(task: TaskDetailResponse) -> str:
    trace_batch_id = task.result_refs.trace_batch_id
    analysis_run_id = task.result_refs.analysis_run_id
    return "\n".join(
        [
            f"task_id: {task.task_id}",
            f"kind: {task.kind}",
            f"lane: {task.lane}",
            f"execution_mode: {task.execution_mode}",
            f"status: {task.status}",
            f"submitted_at: {task.submitted_at}",
            f"owner_user_id: {task.owner_user_id}",
            f"owner_display_name: {task.owner_display_name}",
            f"workspace_id: {task.workspace_id}",
            f"workspace_slug: {task.workspace_slug}",
            f"visibility_scope: {task.visibility_scope}",
            f"dataset_id: {task.dataset_id or '-'}",
            f"definition_id: {task.definition_id if task.definition_id is not None else '-'}",
            f"summary: {task.summary}",
            f"queue_backend: {task.queue_backend}",
            f"worker_task_name: {task.worker_task_name}",
            f"request_ready: {_render_bool(task.request_ready)}",
            f"submitted_from_active_dataset: {_render_bool(task.submitted_from_active_dataset)}",
            f"progress_phase: {task.progress.phase}",
            f"progress_percent_complete: {task.progress.percent_complete}",
            f"progress_summary: {task.progress.summary}",
            f"progress_updated_at: {task.progress.updated_at}",
            f"result_trace_batch_id: {trace_batch_id if trace_batch_id is not None else '-'}",
            f"result_analysis_run_id: {analysis_run_id if analysis_run_id is not None else '-'}",
        ]
    )


def render_circuit_definition_detail(definition: CircuitDefinitionDetailResponse) -> str:
    lines = [
        f"source_definition_id: {definition.definition_id}",
        f"definition_name: {definition.name}",
        f"created_at: {definition.created_at}",
        f"element_count: {definition.element_count}",
        f"validation_status: {definition.validation_status}",
        f"preview_artifact_count: {definition.preview_artifact_count}",
        "preview_artifacts:",
    ]
    lines.extend(f"- {artifact}" for artifact in definition.preview_artifacts)
    lines.extend(
        [
            "source_text:",
            definition.source_text,
            "normalized_output:",
            definition.normalized_output,
            "validation_notices:",
        ]
    )
    lines.extend(f"- [{notice.level}] {notice.message}" for notice in definition.validation_notices)
    return "\n".join(lines)


def render_api_error(error: ApiErrorBodyResponse) -> str:
    suffix = f" [{error.category}/{error.code}]"
    lines = [f"error: {error.message}{suffix}"]
    lines.extend(
        f"field_error: {field_error.field}: {field_error.message}"
        for field_error in error.field_errors
    )
    return "\n".join(lines)


def _render_bool(value: bool) -> str:
    return "true" if value else "false"


def _render_list_line(label: str, parts: Iterable[str]) -> str:
    return f"- {label} | " + " | ".join(parts)
