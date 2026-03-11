from typing import Literal

from pydantic import BaseModel


class MetadataRecordRefResponse(BaseModel):
    backend: Literal["sqlite_metadata"]
    record_type: Literal["dataset", "trace_batch", "analysis_run", "result_handle"]
    record_id: str
    version: int


class TracePayloadRefResponse(BaseModel):
    backend: Literal["local_zarr", "s3_zarr"]
    store_key: str
    store_uri: str
    group_path: str
    array_path: str
    schema_version: str


class ResultHandleRefResponse(BaseModel):
    handle_id: str
    kind: Literal["simulation_trace", "fit_summary", "characterization_report", "plot_bundle"]
    status: Literal["pending", "materialized"]
    label: str
    metadata_record: MetadataRecordRefResponse
    payload_backend: (
        Literal["local_zarr", "json_artifact", "markdown_artifact", "bundle_archive"] | None
    )
    payload_format: Literal["zarr", "json", "markdown", "zip"] | None
    payload_locator: str | None
    provenance_task_id: int | None
