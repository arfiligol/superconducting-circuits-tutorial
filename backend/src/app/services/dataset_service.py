from collections.abc import Sequence
from typing import Protocol

from fastapi import HTTPException, status
from src.app.domain.datasets import (
    DatasetDetail,
    DatasetListQuery,
    DatasetMetadataField,
    DatasetMetadataUpdate,
    DatasetMetadataUpdateResult,
    DatasetSummary,
)


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

    def list_datasets(self, query: DatasetListQuery) -> list[DatasetSummary]:
        datasets = [
            summary
            for summary in self._repository.list_datasets()
            if self._matches_query(summary, query)
        ]
        return self._sort_datasets(datasets, query)

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
    ) -> DatasetMetadataUpdateResult:
        current = self.get_dataset(dataset_id)
        detail = self._repository.update_dataset_metadata(dataset_id, update)
        if detail is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Dataset {dataset_id} was not found.",
            )
        return DatasetMetadataUpdateResult(
            dataset=detail,
            updated_fields=self._updated_fields(current, detail),
        )

    def _matches_query(self, summary: DatasetSummary, query: DatasetListQuery) -> bool:
        if query.family is not None and summary.family.casefold() != query.family.casefold():
            return False
        return query.status is None or summary.status == query.status

    def _sort_datasets(
        self,
        datasets: list[DatasetSummary],
        query: DatasetListQuery,
    ) -> list[DatasetSummary]:
        reverse = query.sort_order == "desc"
        if query.sort_by == "name":
            return sorted(datasets, key=lambda summary: summary.name.casefold(), reverse=reverse)
        if query.sort_by == "samples":
            return sorted(datasets, key=lambda summary: summary.samples, reverse=reverse)
        return sorted(datasets, key=lambda summary: summary.updated_at, reverse=reverse)

    def _updated_fields(
        self,
        current: DatasetDetail,
        updated: DatasetDetail,
    ) -> tuple[DatasetMetadataField, ...]:
        changed_fields: list[DatasetMetadataField] = []
        if current.device_type != updated.device_type:
            changed_fields.append("device_type")
        if current.capabilities != updated.capabilities:
            changed_fields.append("capabilities")
        if current.source != updated.source:
            changed_fields.append("source")
        return tuple(changed_fields)
