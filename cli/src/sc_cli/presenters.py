"""Output formatting helpers for the CLI adapter layer."""

from collections.abc import Iterable, Sequence
from json import dumps
from pathlib import Path

from pydantic import BaseModel
from sc_backend import (
    ApiErrorBodyResponse,
    CircuitDefinitionDetailResponse,
    CircuitDefinitionSummaryResponse,
    DatasetDetailResponse,
    DatasetMetadataUpdateResponse,
    DatasetSummaryResponse,
    SessionResponse,
    TaskDetailResponse,
    TaskSummaryResponse,
)
from sc_core import CircuitDefinitionInspection

from sc_cli.output import OutputMode


def render_preview_artifacts(artifacts: tuple[str, ...]) -> str:
    lines = ["sc_core preview artifacts:"]
    lines.extend(f"- {artifact}" for artifact in artifacts)
    return "\n".join(lines)


def render_circuit_definition_inspection(
    source_file: Path,
    inspection: CircuitDefinitionInspection,
    *,
    output: OutputMode = OutputMode.TEXT,
) -> str:
    if output is OutputMode.JSON:
        return _render_json_payload(
            {
                "source_file": str(source_file),
                "circuit_name": inspection.circuit_name,
                "family": inspection.family,
                "element_count": inspection.element_count,
                "normalized_output": inspection.normalized_output,
                "validation_notices": [
                    {"level": notice.level, "message": notice.message}
                    for notice in inspection.validation_notices
                ],
            }
        )
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


def render_circuit_definition_summaries(
    definitions: list[CircuitDefinitionSummaryResponse],
    *,
    output: OutputMode = OutputMode.TEXT,
) -> str:
    if output is OutputMode.JSON:
        return _render_json_models(definitions)
    lines = [f"circuit_definitions: {len(definitions)}"]
    lines.extend(
        _render_list_line(
            f"#{definition.definition_id}",
            (
                definition.name,
                f"created_at={definition.created_at}",
                f"elements={definition.element_count}",
                f"validation={definition.validation_status}",
                f"preview_artifacts={definition.preview_artifact_count}",
            ),
        )
        for definition in definitions
    )
    return "\n".join(lines)


def render_session(session: SessionResponse, *, output: OutputMode = OutputMode.TEXT) -> str:
    if output is OutputMode.JSON:
        return _render_json_model(session)
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


def render_session_identity(
    session: SessionResponse,
    *,
    output: OutputMode = OutputMode.TEXT,
) -> str:
    if output is OutputMode.JSON:
        return _render_json_payload(
            {
                "session_id": session.session_id,
                "auth": session.auth.model_dump(mode="json"),
                "identity": (
                    None if session.identity is None else session.identity.model_dump(mode="json")
                ),
            }
        )
    lines = [
        f"session_id: {session.session_id}",
        f"auth_state: {session.auth.state}",
        f"auth_mode: {session.auth.mode}",
        f"scopes: {', '.join(session.auth.scopes) if session.auth.scopes else '(none)'}",
        f"can_submit_tasks: {_render_bool(session.auth.can_submit_tasks)}",
        f"can_manage_datasets: {_render_bool(session.auth.can_manage_datasets)}",
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
    return "\n".join(lines)


def render_session_workspace(
    session: SessionResponse,
    *,
    output: OutputMode = OutputMode.TEXT,
) -> str:
    if output is OutputMode.JSON:
        return _render_json_model(session.workspace)
    lines = [
        f"workspace_id: {session.workspace.workspace_id}",
        f"workspace_slug: {session.workspace.slug}",
        f"workspace_display_name: {session.workspace.display_name}",
        f"workspace_role: {session.workspace.role}",
        f"default_task_scope: {session.workspace.default_task_scope}",
    ]
    lines.extend(_render_active_dataset_lines(session))
    return "\n".join(lines)


def render_session_active_dataset(
    session: SessionResponse,
    *,
    output: OutputMode = OutputMode.TEXT,
) -> str:
    if output is OutputMode.JSON:
        return _render_json_payload(
            {
                "active_dataset": (
                    None
                    if session.workspace.active_dataset is None
                    else session.workspace.active_dataset.model_dump(mode="json")
                )
            }
        )
    return "\n".join(_render_active_dataset_lines(session))


def render_dataset_summaries(
    datasets: list[DatasetSummaryResponse],
    *,
    output: OutputMode = OutputMode.TEXT,
) -> str:
    if output is OutputMode.JSON:
        return _render_json_models(datasets)
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


def render_dataset_detail(
    dataset: DatasetDetailResponse,
    *,
    output: OutputMode = OutputMode.TEXT,
) -> str:
    if output is OutputMode.JSON:
        return _render_json_model(dataset)
    lines = [
        f"dataset_id: {dataset.dataset_id}",
        f"name: {dataset.name}",
        f"family: {dataset.family}",
        f"owner: {dataset.owner}",
        f"status: {dataset.status}",
        f"device_type: {dataset.device_type}",
        f"source: {dataset.source}",
        f"samples: {dataset.samples}",
        f"updated_at: {dataset.updated_at}",
        f"capability_count: {dataset.capability_count}",
        f"tag_count: {dataset.tag_count}",
        "capabilities:",
    ]
    lines.extend(f"- {capability}" for capability in dataset.capabilities)
    lines.extend(["tags:"])
    lines.extend(f"- {tag}" for tag in dataset.tags)
    lines.extend(
        [
            (
                "preview_columns: "
                f"{', '.join(dataset.preview_columns) if dataset.preview_columns else '-'}"
            ),
            "preview_rows:",
        ]
    )
    lines.extend(f"- {', '.join(row)}" for row in dataset.preview_rows)
    lines.extend(["artifacts:"])
    lines.extend(f"- {artifact}" for artifact in dataset.artifacts)
    lines.extend(["lineage:"])
    lines.extend(f"- {item}" for item in dataset.lineage)
    lines.extend(
        [
            f"metrics_capability_count: {dataset.metrics.capability_count}",
            f"metrics_tag_count: {dataset.metrics.tag_count}",
            f"metrics_preview_row_count: {dataset.metrics.preview_row_count}",
            f"metrics_artifact_count: {dataset.metrics.artifact_count}",
            f"metrics_lineage_depth: {dataset.metrics.lineage_depth}",
            f"storage_metadata_record_id: {dataset.storage.metadata_record.record_id}",
            (f"storage_primary_trace_store_uri: {_render_primary_trace_store_uri(dataset)}"),
            f"storage_result_handle_count: {len(dataset.storage.result_handles)}",
        ]
    )
    return "\n".join(lines)


def render_dataset_metadata_update(
    result: DatasetMetadataUpdateResponse,
    *,
    output: OutputMode = OutputMode.TEXT,
) -> str:
    if output is OutputMode.JSON:
        return _render_json_model(result)
    lines = [
        (
            "updated_fields: "
            f"{', '.join(result.updated_fields) if result.updated_fields else '(none)'}"
        ),
        render_dataset_detail(result.dataset, output=OutputMode.TEXT),
    ]
    return "\n".join(lines)


def render_task_summaries(
    tasks: list[TaskSummaryResponse],
    *,
    output: OutputMode = OutputMode.TEXT,
) -> str:
    if output is OutputMode.JSON:
        return _render_json_models(tasks)
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


def render_task_detail(task: TaskDetailResponse, *, output: OutputMode = OutputMode.TEXT) -> str:
    if output is OutputMode.JSON:
        return _render_json_model(task)
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


def render_circuit_definition_detail(
    definition: CircuitDefinitionDetailResponse,
    *,
    output: OutputMode = OutputMode.TEXT,
) -> str:
    if output is OutputMode.JSON:
        return _render_json_model(definition)
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


def render_circuit_definition_delete_result(
    definition_id: int,
    *,
    output: OutputMode = OutputMode.TEXT,
) -> str:
    if output is OutputMode.JSON:
        return _render_json_payload({"operation": "deleted", "definition_id": definition_id})
    return "\n".join(
        [
            "operation: deleted",
            f"definition_id: {definition_id}",
        ]
    )


def render_api_error(error: ApiErrorBodyResponse, *, output: OutputMode = OutputMode.TEXT) -> str:
    if output is OutputMode.JSON:
        return _render_json_payload({"error": error.model_dump(mode="json")})
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


def _render_primary_trace_store_uri(dataset: DatasetDetailResponse) -> str:
    if dataset.storage.primary_trace is None:
        return "-"
    return dataset.storage.primary_trace.store_uri


def _render_active_dataset_lines(session: SessionResponse) -> list[str]:
    if session.workspace.active_dataset is None:
        return ["active_dataset: none"]
    return [
        f"active_dataset_id: {session.workspace.active_dataset.dataset_id}",
        f"active_dataset_name: {session.workspace.active_dataset.name}",
        f"active_dataset_family: {session.workspace.active_dataset.family}",
        f"active_dataset_status: {session.workspace.active_dataset.status}",
        f"active_dataset_owner: {session.workspace.active_dataset.owner}",
        f"active_dataset_access_scope: {session.workspace.active_dataset.access_scope}",
    ]


def _render_json_model(model: BaseModel) -> str:
    return model.model_dump_json(indent=2)


def _render_json_models(models: Sequence[BaseModel]) -> str:
    return _render_json_payload([model.model_dump(mode="json") for model in models])


def _render_json_payload(payload: object) -> str:
    return dumps(payload, indent=2)
