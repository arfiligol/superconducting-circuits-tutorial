from dataclasses import dataclass
from typing import Literal

MetadataBackend = Literal["sqlite_metadata"]
MetadataRecordType = Literal["dataset", "trace_batch", "analysis_run", "result_handle"]
TracePayloadBackend = Literal["local_zarr", "s3_zarr"]
ResultPayloadBackend = Literal["local_zarr", "json_artifact", "markdown_artifact", "bundle_archive"]
ResultPayloadFormat = Literal["zarr", "json", "markdown", "zip"]
ResultHandleKind = Literal[
    "simulation_trace",
    "fit_summary",
    "characterization_report",
    "plot_bundle",
]
ResultHandleStatus = Literal["pending", "materialized"]


@dataclass(frozen=True)
class MetadataRecordRef:
    backend: MetadataBackend
    record_type: MetadataRecordType
    record_id: str
    version: int


@dataclass(frozen=True)
class TracePayloadRef:
    backend: TracePayloadBackend
    store_key: str
    store_uri: str
    group_path: str
    array_path: str
    schema_version: str


@dataclass(frozen=True)
class ResultHandleRef:
    handle_id: str
    kind: ResultHandleKind
    status: ResultHandleStatus
    label: str
    metadata_record: MetadataRecordRef
    payload_backend: ResultPayloadBackend | None
    payload_format: ResultPayloadFormat | None
    payload_locator: str | None
    provenance_task_id: int | None

