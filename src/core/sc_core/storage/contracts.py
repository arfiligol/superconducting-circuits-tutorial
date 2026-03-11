from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Literal, cast

from sc_core.execution import TaskResultHandle

STORAGE_CONTRACT_VERSION = "sc_storage.v1"
TraceStoreBackend = Literal["local_zarr", "s3_zarr"]
StorageRecordKind = Literal["trace_batch", "analysis_run"]


@dataclass(frozen=True)
class StorageRecordHandle:
    """Canonical reference to one persisted execution/storage record."""

    kind: StorageRecordKind
    record_id: int

    def to_payload(self) -> dict[str, object]:
        return {
            "kind": self.kind,
            "record_id": self.record_id,
        }


@dataclass(frozen=True)
class TraceResultLinkage:
    """Storage-facing linkage between task outputs and persisted record handles."""

    trace_batch: StorageRecordHandle | None = None
    analysis_run: StorageRecordHandle | None = None

    @classmethod
    def from_result_handle(cls, result_handle: TaskResultHandle) -> TraceResultLinkage:
        return cls(
            trace_batch=(
                StorageRecordHandle(kind="trace_batch", record_id=result_handle.trace_batch_id)
                if result_handle.trace_batch_id is not None
                else None
            ),
            analysis_run=(
                StorageRecordHandle(kind="analysis_run", record_id=result_handle.analysis_run_id)
                if result_handle.analysis_run_id is not None
                else None
            ),
        )

    def has_outputs(self) -> bool:
        return self.trace_batch is not None or self.analysis_run is not None

    def output_handles(self) -> tuple[StorageRecordHandle, ...]:
        handles: list[StorageRecordHandle] = []
        if self.trace_batch is not None:
            handles.append(self.trace_batch)
        if self.analysis_run is not None:
            handles.append(self.analysis_run)
        return tuple(handles)

    def to_payload(self) -> dict[str, int]:
        payload: dict[str, int] = {}
        if self.trace_batch is not None:
            payload["trace_batch_id"] = self.trace_batch.record_id
        if self.analysis_run is not None:
            payload["analysis_run_id"] = self.analysis_run.record_id
        return payload


@dataclass(frozen=True)
class TraceStoreLocator:
    """Canonical value object for one persisted TraceStore locator."""

    backend: TraceStoreBackend
    store_key: str
    group_path: str
    array_path: str
    dtype: str
    shape: tuple[int, ...]
    chunk_shape: tuple[int, ...]
    schema_version: str
    store_uri: str | None = None

    @classmethod
    def from_mapping(cls, payload: Mapping[str, object]) -> TraceStoreLocator:
        backend = _coerce_backend(payload.get("backend"))
        store_key = _require_str(payload.get("store_key"), field_name="store_key")
        group_path = _require_str(payload.get("group_path"), field_name="group_path")
        array_path = _require_str(payload.get("array_path"), field_name="array_path")
        dtype = _require_str(payload.get("dtype"), field_name="dtype")
        schema_version = _require_str(payload.get("schema_version"), field_name="schema_version")
        shape = _coerce_int_tuple(payload.get("shape"), field_name="shape")
        chunk_shape = _coerce_int_tuple(payload.get("chunk_shape"), field_name="chunk_shape")
        store_uri = _optional_str(payload.get("store_uri"))
        return cls(
            backend=backend,
            store_key=store_key,
            group_path=group_path,
            array_path=array_path,
            dtype=dtype,
            shape=shape,
            chunk_shape=chunk_shape,
            schema_version=schema_version,
            store_uri=store_uri,
        )

    def to_payload(self) -> dict[str, object]:
        payload: dict[str, object] = {
            "contract_version": STORAGE_CONTRACT_VERSION,
            "backend": self.backend,
            "store_key": self.store_key,
            "group_path": self.group_path,
            "array_path": self.array_path,
            "dtype": self.dtype,
            "shape": list(self.shape),
            "chunk_shape": list(self.chunk_shape),
            "schema_version": self.schema_version,
        }
        if self.store_uri is not None:
            payload["store_uri"] = self.store_uri
        return payload


@dataclass(frozen=True)
class TraceBatchProvenance:
    """Canonical provenance view derived from trace-batch snapshot payloads."""

    source_kind: str
    stage_kind: str
    parent_batch_id: int | None = None
    setup_kind: str | None = None
    setup_version: str | None = None
    source_batch_id: int | None = None
    run_kind: str | None = None

    @classmethod
    def from_snapshot(cls, snapshot: Mapping[str, object]) -> TraceBatchProvenance:
        provenance_payload = _mapping(snapshot.get("provenance_payload"))
        setup_payload = _mapping(snapshot.get("setup_payload"))
        summary_payload = _mapping(snapshot.get("summary_payload"))
        source_kind = _first_non_empty_str(
            snapshot.get("source_kind"),
            provenance_payload.get("source_kind"),
        )
        stage_kind = _first_non_empty_str(
            snapshot.get("stage_kind"),
            provenance_payload.get("stage_kind"),
        )
        if source_kind is None:
            raise ValueError("TraceBatch snapshot is missing source_kind.")
        if stage_kind is None:
            raise ValueError("TraceBatch snapshot is missing stage_kind.")
        return cls(
            source_kind=source_kind,
            stage_kind=stage_kind,
            parent_batch_id=_optional_int(snapshot.get("parent_batch_id")),
            setup_kind=_first_non_empty_str(
                snapshot.get("setup_kind"),
                setup_payload.get("setup_kind"),
            ),
            setup_version=_first_non_empty_str(
                snapshot.get("setup_version"),
                setup_payload.get("setup_version"),
            ),
            source_batch_id=_optional_int(
                provenance_payload.get("source_batch_id")
                if provenance_payload.get("source_batch_id") is not None
                else provenance_payload.get("source_simulation_bundle_id")
            ),
            run_kind=_first_non_empty_str(
                summary_payload.get("run_kind"),
                provenance_payload.get("run_kind"),
            ),
        )

    def to_payload(self) -> dict[str, object]:
        payload: dict[str, object] = {
            "contract_version": STORAGE_CONTRACT_VERSION,
            "source_kind": self.source_kind,
            "stage_kind": self.stage_kind,
        }
        if self.parent_batch_id is not None:
            payload["parent_batch_id"] = self.parent_batch_id
        if self.setup_kind is not None:
            payload["setup_kind"] = self.setup_kind
        if self.setup_version is not None:
            payload["setup_version"] = self.setup_version
        if self.source_batch_id is not None:
            payload["source_batch_id"] = self.source_batch_id
        if self.run_kind is not None:
            payload["run_kind"] = self.run_kind
        return payload


@dataclass(frozen=True)
class TraceBatchHandle:
    """Canonical trace-batch handle enriched with provenance metadata."""

    trace_batch_id: int
    design_id: int
    status: str
    provenance: TraceBatchProvenance

    @classmethod
    def from_snapshot(cls, snapshot: Mapping[str, object]) -> TraceBatchHandle:
        return cls(
            trace_batch_id=_require_int(snapshot.get("id"), field_name="id"),
            design_id=_require_int(snapshot.get("design_id"), field_name="design_id"),
            status=_require_str(snapshot.get("status"), field_name="status"),
            provenance=TraceBatchProvenance.from_snapshot(snapshot),
        )

    def to_payload(self) -> dict[str, object]:
        return {
            "contract_version": STORAGE_CONTRACT_VERSION,
            "trace_batch_id": self.trace_batch_id,
            "design_id": self.design_id,
            "status": self.status,
            "provenance": self.provenance.to_payload(),
        }


def _mapping(value: object) -> Mapping[str, object]:
    return value if isinstance(value, Mapping) else {}


def _coerce_backend(value: object) -> TraceStoreBackend:
    backend = _require_str(value, field_name="backend")
    if backend not in {"local_zarr", "s3_zarr"}:
        raise ValueError(f"Unsupported TraceStore backend: {backend}")
    return cast(TraceStoreBackend, backend)


def _coerce_int_tuple(value: object, *, field_name: str) -> tuple[int, ...]:
    if not isinstance(value, list) or not value:
        raise ValueError(f"TraceStoreLocator.{field_name} is required.")
    return tuple(_require_int(item, field_name=field_name) for item in value)


def _require_int(value: object, *, field_name: str) -> int:
    if isinstance(value, bool) or value is None:
        raise ValueError(f"{field_name} is required.")
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        text = value.strip()
        if text:
            return int(text)
    raise ValueError(f"{field_name} must be an integer.")


def _optional_int(value: object) -> int | None:
    if value is None:
        return None
    if isinstance(value, bool):
        raise ValueError("Expected integer-compatible value.")
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        text = value.strip()
        if text:
            return int(text)
    raise ValueError("Expected integer-compatible value.")


def _require_str(value: object, *, field_name: str) -> str:
    text = _optional_str(value)
    if text is None:
        raise ValueError(f"{field_name} is required.")
    return text


def _optional_str(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _first_non_empty_str(*values: object) -> str | None:
    for value in values:
        text = _optional_str(value)
        if text is not None:
            return text
    return None
