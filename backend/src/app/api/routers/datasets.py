from typing import Annotated

from fastapi import APIRouter, Depends
from src.app.api.schemas.datasets import (
    DatasetDetailResponse,
    DatasetMetadataUpdateRequest,
    DatasetSummaryResponse,
)
from src.app.domain.datasets import DatasetMetadataUpdate
from src.app.infrastructure.runtime import get_dataset_service
from src.app.services.dataset_service import DatasetService

router = APIRouter(prefix="/datasets", tags=["datasets"])


@router.get("", response_model=list[DatasetSummaryResponse])
def list_datasets(
    dataset_service: Annotated[DatasetService, Depends(get_dataset_service)],
) -> list[DatasetSummaryResponse]:
    return [
        DatasetSummaryResponse.model_validate(summary.__dict__)
        for summary in dataset_service.list_datasets()
    ]


@router.get("/{dataset_id}", response_model=DatasetDetailResponse)
def get_dataset(
    dataset_id: str,
    dataset_service: Annotated[DatasetService, Depends(get_dataset_service)],
) -> DatasetDetailResponse:
    detail = dataset_service.get_dataset(dataset_id)
    return DatasetDetailResponse(
        dataset_id=detail.dataset_id,
        name=detail.name,
        family=detail.family,
        owner=detail.owner,
        updated_at=detail.updated_at,
        samples=detail.samples,
        status=detail.status,
        device_type=detail.device_type,
        capabilities=list(detail.capabilities),
        source=detail.source,
        tags=list(detail.tags),
        preview_columns=list(detail.preview_columns),
        preview_rows=[list(row) for row in detail.preview_rows],
        artifacts=list(detail.artifacts),
        lineage=list(detail.lineage),
    )


@router.patch("/{dataset_id}/metadata", response_model=DatasetDetailResponse)
def update_dataset_metadata(
    dataset_id: str,
    payload: DatasetMetadataUpdateRequest,
    dataset_service: Annotated[DatasetService, Depends(get_dataset_service)],
) -> DatasetDetailResponse:
    detail = dataset_service.update_dataset_metadata(
        dataset_id,
        DatasetMetadataUpdate(
            device_type=payload.device_type,
            capabilities=tuple(payload.capabilities),
            source=payload.source,
        ),
    )
    return get_dataset(detail.dataset_id, dataset_service)
