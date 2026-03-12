from dataclasses import replace
from typing import Protocol

from sc_core.execution import TaskResultHandle

from src.app.domain.storage import MetadataRecordRef, ResultHandleRef, TracePayloadRef
from src.app.domain.tasks import TaskCreateDraft, TaskDetail, TaskLifecycleUpdate, TaskResultRefs
from src.app.infrastructure.rewrite_app_state_repository import (
    build_pending_result_refs,
    build_seed_tasks,
)


class StorageMetadataRepository(Protocol):
    def get_storage_record(self, record_id: str) -> MetadataRecordRef | None: ...

    def get_trace_payload_for_owner_record(
        self,
        owner_record_id: str,
    ) -> TracePayloadRef | None: ...

    def get_result_handle(self, handle_id: str) -> ResultHandleRef | None: ...

    def list_result_handles_for_task(self, task_id: int) -> tuple[ResultHandleRef, ...]: ...

    def save_storage_record(self, record: MetadataRecordRef) -> MetadataRecordRef: ...

    def save_trace_payload(
        self,
        owner_record: MetadataRecordRef,
        trace_payload: TracePayloadRef,
        *,
        writer_version: str | None = None,
    ) -> TracePayloadRef: ...

    def save_result_handle(self, result_handle: ResultHandleRef) -> ResultHandleRef: ...


class TaskSnapshotRepository(Protocol):
    def has_tasks(self) -> bool: ...

    def list_tasks(self) -> tuple[TaskDetail, ...]: ...

    def get_task(self, task_id: int) -> TaskDetail | None: ...

    def create_task(self, draft: TaskCreateDraft) -> TaskDetail: ...

    def save_task_snapshot(self, task: TaskDetail) -> TaskDetail: ...


class PersistedRewriteTaskRepository:
    def __init__(
        self,
        task_snapshot_repository: TaskSnapshotRepository,
        storage_metadata_repository: StorageMetadataRepository,
    ) -> None:
        self._task_snapshot_repository = task_snapshot_repository
        self._storage_metadata_repository = storage_metadata_repository
        self._seed_tasks = build_seed_tasks()
        self._ensure_seed_task_snapshots()
        self._ensure_seed_storage_metadata()

    def list_tasks(self) -> tuple[TaskDetail, ...]:
        return tuple(
            self._hydrate_task(task) for task in self._task_snapshot_repository.list_tasks()
        )

    def get_task(self, task_id: int) -> TaskDetail | None:
        task = self._task_snapshot_repository.get_task(task_id)
        if task is None:
            return None
        return self._hydrate_task(task)

    def create_task(self, draft: TaskCreateDraft) -> TaskDetail:
        task_snapshot = self._task_snapshot_repository.create_task(draft)
        task_with_result_refs = replace(
            task_snapshot,
            result_refs=build_pending_result_refs(
                task_id=task_snapshot.task_id,
                draft=draft,
            ),
        )
        self._persist_result_refs(task_with_result_refs.result_refs)
        return self._hydrate_task(task_with_result_refs)

    def update_task_lifecycle(self, update: TaskLifecycleUpdate) -> TaskDetail | None:
        current_task = self.get_task(update.task_id)
        if current_task is None:
            return None

        persisted_snapshot = self._task_snapshot_repository.save_task_snapshot(
            replace(
                current_task,
                status=update.status,
                summary=update.summary or current_task.summary,
                progress=replace(
                    current_task.progress,
                    phase=update.status,
                    percent_complete=update.progress_percent_complete,
                    summary=update.progress_summary,
                    updated_at=update.progress_updated_at,
                ),
            )
        )

        effective_result_refs = update.result_refs or current_task.result_refs
        if update.result_refs is not None:
            self._persist_result_refs(update.result_refs)

        return self._hydrate_task(replace(persisted_snapshot, result_refs=effective_result_refs))

    def _ensure_seed_task_snapshots(self) -> None:
        if self._task_snapshot_repository.has_tasks():
            return

        for task in self._seed_tasks:
            self._task_snapshot_repository.save_task_snapshot(task)

    def _ensure_seed_storage_metadata(self) -> None:
        for task in self._seed_tasks:
            self._ensure_result_refs(task.result_refs)

    def _persist_result_refs(self, result_refs: TaskResultRefs) -> None:
        for record in result_refs.metadata_records:
            self._storage_metadata_repository.save_storage_record(record)

        trace_owner_record = _trace_owner_record(result_refs)
        if result_refs.trace_payload is not None and trace_owner_record is not None:
            self._storage_metadata_repository.save_trace_payload(
                trace_owner_record,
                result_refs.trace_payload,
                writer_version="rewrite-backend.runtime",
            )

        for result_handle in result_refs.result_handles:
            self._storage_metadata_repository.save_result_handle(result_handle)

    def _ensure_result_refs(self, result_refs: TaskResultRefs) -> None:
        for record in result_refs.metadata_records:
            if self._storage_metadata_repository.get_storage_record(record.record_id) is None:
                self._storage_metadata_repository.save_storage_record(record)

        trace_owner_record = _trace_owner_record(result_refs)
        if (
            result_refs.trace_payload is not None
            and trace_owner_record is not None
            and self._storage_metadata_repository.get_trace_payload_for_owner_record(
                trace_owner_record.record_id
            )
            is None
        ):
            self._storage_metadata_repository.save_trace_payload(
                trace_owner_record,
                result_refs.trace_payload,
                writer_version="rewrite-backend.runtime",
            )

        for result_handle in result_refs.result_handles:
            if self._storage_metadata_repository.get_result_handle(result_handle.handle_id) is None:
                self._storage_metadata_repository.save_result_handle(result_handle)

    def _hydrate_task(self, task: TaskDetail) -> TaskDetail:
        persisted_result_handles = self._storage_metadata_repository.list_result_handles_for_task(
            task.task_id
        )
        if len(persisted_result_handles) == 0:
            return task

        primary_result_handle = persisted_result_handles[0]
        owner_record = (
            primary_result_handle.provenance.trace_batch_record
            or primary_result_handle.provenance.analysis_run_record
        )
        trace_payload = task.result_refs.trace_payload
        if owner_record is not None:
            trace_payload = (
                self._storage_metadata_repository.get_trace_payload_for_owner_record(
                    owner_record.record_id
                )
                or trace_payload
            )
        metadata_records = _build_metadata_records_for_hydration(
            owner_record=owner_record,
            primary_result_handle=primary_result_handle,
        )
        return replace(
            task,
            result_refs=TaskResultRefs(
                result_handle=_build_storage_linkage_handle(
                    owner_record=owner_record,
                    current_handle=task.result_refs.result_handle,
                ),
                metadata_records=metadata_records,
                trace_payload=trace_payload,
                result_handles=persisted_result_handles,
            ),
        )


def _trace_owner_record(result_refs: TaskResultRefs) -> MetadataRecordRef | None:
    if result_refs.trace_payload is None:
        return None

    for record in result_refs.metadata_records:
        if record.record_type in {"trace_batch", "analysis_run", "dataset"}:
            return record
    return None


def _build_storage_linkage_handle(
    *,
    owner_record: MetadataRecordRef | None,
    current_handle: TaskResultHandle,
) -> TaskResultHandle:
    if owner_record is None:
        return current_handle
    if owner_record.record_type == "trace_batch":
        return TaskResultHandle(trace_batch_id=_parse_record_suffix(owner_record.record_id))
    if owner_record.record_type == "analysis_run":
        return TaskResultHandle(analysis_run_id=_parse_record_suffix(owner_record.record_id))
    return current_handle


def _build_metadata_records_for_hydration(
    *,
    owner_record: MetadataRecordRef | None,
    primary_result_handle: ResultHandleRef,
) -> tuple[MetadataRecordRef, ...]:
    metadata_records: list[MetadataRecordRef] = []
    if owner_record is not None:
        metadata_records.append(owner_record)
    metadata_records.append(primary_result_handle.metadata_record)
    return tuple(_dedupe_metadata_records(metadata_records))


def _dedupe_metadata_records(
    records: list[MetadataRecordRef],
) -> list[MetadataRecordRef]:
    deduped: dict[str, MetadataRecordRef] = {}
    for record in records:
        deduped.setdefault(record.record_id, record)
    return list(deduped.values())


def _parse_record_suffix(record_id: str) -> int:
    _, _, suffix = record_id.partition(":")
    return int(suffix)
