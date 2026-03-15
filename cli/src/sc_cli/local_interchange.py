"""CLI-local interchange bundle contracts."""

from __future__ import annotations

from pydantic import BaseModel

from sc_cli.local_runtime import LocalTaskDetail, LocalTaskResultRefs


class LocalBundleMetadata(BaseModel):
    bundle_family: str
    bundle_version: str
    bundle_id: str
    exported_at: str
    source_runtime: str


class LocalResultBundleTask(BaseModel):
    task_id: int
    kind: str
    lane: str
    execution_mode: str
    status: str
    dataset_id: str | None = None
    definition_id: int | None = None
    summary: str


class LocalResultBundle(BaseModel):
    metadata: LocalBundleMetadata
    task: LocalResultBundleTask
    result_refs: LocalTaskResultRefs


class LocalResultBundleExportReceipt(BaseModel):
    bundle_file: str
    bundle: LocalResultBundle


class LocalResultBundleImportReceipt(BaseModel):
    bundle_file: str
    bundle: LocalResultBundle
    imported_task: LocalTaskDetail


def build_result_bundle(task: LocalTaskDetail) -> LocalResultBundle:
    return LocalResultBundle(
        metadata=LocalBundleMetadata(
            bundle_family="result_bundle",
            bundle_version="1.0",
            bundle_id=f"bundle:result:{task.task_id}",
            exported_at="2026-03-15T12:00:00Z",
            source_runtime="standalone_cli",
        ),
        task=LocalResultBundleTask(
            task_id=task.task_id,
            kind=task.kind,
            lane=task.lane,
            execution_mode=task.execution_mode,
            status=task.status,
            dataset_id=task.dataset_id,
            definition_id=task.definition_id,
            summary=task.summary,
        ),
        result_refs=task.result_refs.model_copy(deep=True),
    )
