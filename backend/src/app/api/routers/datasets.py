from typing import Annotated

from fastapi import APIRouter, Depends, Query

from src.app.api.schemas.datasets import (
    DatasetDetailResponse,
    DatasetMetadataUpdateRequest,
    DatasetMetadataUpdateResponse,
    DatasetMetricsResponse,
    DatasetSummaryResponse,
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
    )
