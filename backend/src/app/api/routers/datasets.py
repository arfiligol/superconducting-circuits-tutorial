from typing import Annotated

from fastapi import APIRouter, Depends, Query

from src.app.api.schemas.datasets import (
    DatasetDetailResponse,
    DatasetMetadataUpdateRequest,
    DatasetMetadataUpdateResponse,
    DatasetMetricsResponse,
    DatasetStorageResponse,
    DatasetSummaryResponse,
)
from src.app.api.schemas.storage import (
    MetadataRecordRefResponse,
    ResultHandleRefResponse,
    TracePayloadRefResponse,
)
from src.app.domain.datasets import (
    DatasetDetail,
    DatasetListQuery,
    DatasetMetadataUpdate,
    DatasetSortBy,
    DatasetStatus,
    DatasetSummary,
    SortOrder,
)
from src.app.domain.storage import MetadataRecordRef, ResultHandleRef, TracePayloadRef
from src.app.infrastructure.runtime import get_dataset_service
from src.app.services.dataset_service import DatasetService

router = APIRouter(prefix="/datasets", tags=["datasets"])


@router.get("", response_model=list[DatasetSummaryResponse])
def list_datasets(
    dataset_service: Annotated[DatasetService, Depends(get_dataset_service)],
    family: Annotated[str | None, Query(min_length=1)] = None,
    status: Annotated[DatasetStatus | None, Query()] = None,
    sort_by: Annotated[DatasetSortBy, Query()] = "updated_at",
    sort_order: Annotated[SortOrder, Query()] = "desc",
) -> list[DatasetSummaryResponse]:
    return [
        _build_dataset_summary_response(summary)
        for summary in dataset_service.list_datasets(
            DatasetListQuery(
                family=family,
                status=status,
                sort_by=sort_by,
                sort_order=sort_order,
            ),
        )
    ]


@router.get("/{dataset_id}", response_model=DatasetDetailResponse)
def get_dataset(
    dataset_id: str,
    dataset_service: Annotated[DatasetService, Depends(get_dataset_service)],
) -> DatasetDetailResponse:
    detail = dataset_service.get_dataset(dataset_id)
    return _build_dataset_detail_response(detail)


@router.patch("/{dataset_id}/metadata", response_model=DatasetMetadataUpdateResponse)
def update_dataset_metadata(
    dataset_id: str,
    payload: DatasetMetadataUpdateRequest,
    dataset_service: Annotated[DatasetService, Depends(get_dataset_service)],
) -> DatasetMetadataUpdateResponse:
    result = dataset_service.update_dataset_metadata(
        dataset_id,
        DatasetMetadataUpdate(
            device_type=payload.device_type,
            capabilities=tuple(payload.capabilities),
            source=payload.source,
        ),
    )
    return DatasetMetadataUpdateResponse(
        dataset=_build_dataset_detail_response(result.dataset),
        updated_fields=list(result.updated_fields),
    )


def _build_dataset_summary_response(summary: DatasetSummary) -> DatasetSummaryResponse:
    return DatasetSummaryResponse.model_validate(summary.__dict__)


def _build_dataset_detail_response(detail: DatasetDetail) -> DatasetDetailResponse:
    return DatasetDetailResponse(
        dataset_id=detail.dataset_id,
        name=detail.name,
        family=detail.family,
        owner=detail.owner,
        updated_at=detail.updated_at,
        device_type=detail.device_type,
        source=detail.source,
        samples=detail.samples,
        status=detail.status,
        capability_count=len(detail.capabilities),
        tag_count=len(detail.tags),
        capabilities=list(detail.capabilities),
        tags=list(detail.tags),
        preview_columns=list(detail.preview_columns),
        preview_rows=[list(row) for row in detail.preview_rows],
        artifacts=list(detail.artifacts),
        lineage=list(detail.lineage),
        metrics=DatasetMetricsResponse(
            capability_count=len(detail.capabilities),
            tag_count=len(detail.tags),
            preview_row_count=len(detail.preview_rows),
            artifact_count=len(detail.artifacts),
            lineage_depth=len(detail.lineage),
        ),
        storage=DatasetStorageResponse(
            metadata_record=_build_metadata_record_ref_response(detail.metadata_record),
            primary_trace=_build_trace_payload_ref_response(detail.primary_trace),
            result_handles=[
                _build_result_handle_ref_response(handle) for handle in detail.result_handles
            ],
        ),
    )


def _build_metadata_record_ref_response(
    record: MetadataRecordRef,
) -> MetadataRecordRefResponse:
    return MetadataRecordRefResponse(
        backend=record.backend,
        record_type=record.record_type,
        record_id=record.record_id,
        version=record.version,
    )


def _build_trace_payload_ref_response(
    trace_payload: TracePayloadRef | None,
) -> TracePayloadRefResponse | None:
    if trace_payload is None:
        return None
    return TracePayloadRefResponse(
        backend=trace_payload.backend,
        store_key=trace_payload.store_key,
        store_uri=trace_payload.store_uri,
        group_path=trace_payload.group_path,
        array_path=trace_payload.array_path,
        schema_version=trace_payload.schema_version,
    )


def _build_result_handle_ref_response(
    handle: ResultHandleRef,
) -> ResultHandleRefResponse:
    return ResultHandleRefResponse(
        handle_id=handle.handle_id,
        kind=handle.kind,
        status=handle.status,
        label=handle.label,
        metadata_record=_build_metadata_record_ref_response(handle.metadata_record),
        payload_backend=handle.payload_backend,
        payload_format=handle.payload_format,
        payload_locator=handle.payload_locator,
        provenance_task_id=handle.provenance_task_id,
    )
