from collections.abc import Sequence
from typing import Protocol

from fastapi import HTTPException, status
from src.app.domain.datasets import DatasetDetail, DatasetMetadataUpdate, DatasetSummary


class DatasetRepository(Protocol):
    def list_datasets(self) -> Sequence[DatasetSummary]: ...

    def get_dataset(self, dataset_id: str) -> DatasetDetail | None: ...

    def update_dataset_metadata(
        self,
        dataset_id: str,
        update: DatasetMetadataUpdate,
    ) -> DatasetDetail | None: ...


class DatasetService:
    def __init__(self, repository: DatasetRepository) -> None:
        self._repository = repository

    def list_datasets(self) -> list[DatasetSummary]:
        return list(self._repository.list_datasets())

    def get_dataset(self, dataset_id: str) -> DatasetDetail:
        detail = self._repository.get_dataset(dataset_id)
        if detail is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Dataset {dataset_id} was not found.",
            )
        return detail

    def update_dataset_metadata(
        self,
        dataset_id: str,
        update: DatasetMetadataUpdate,
    ) -> DatasetDetail:
        detail = self._repository.update_dataset_metadata(dataset_id, update)
        if detail is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Dataset {dataset_id} was not found.",
            )
        return detail
