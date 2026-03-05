"""Repository contracts used by page/application orchestration layers."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from core.shared.persistence.repositories.query_objects import TraceIndexPageQuery

TraceIndexRow = dict[str, str | int]


@runtime_checkable
class DataRecordCharacterizationContract(Protocol):
    """Minimal DataRecord repository API required by characterization/runtime flows."""

    def count_by_dataset(self, dataset_id: int) -> int: ...

    def list_distinct_index_for_profile(self, dataset_id: int) -> list[dict[str, str]]: ...

    def list_index_page_by_dataset(
        self,
        dataset_id: int,
        *,
        query: TraceIndexPageQuery | None = None,
        **kwargs: object,
    ) -> tuple[list[TraceIndexRow], int]: ...


@runtime_checkable
class ResultBundleCharacterizationContract(Protocol):
    """Minimal ResultBundle repository API required by characterization/runtime flows."""

    def count_data_records(self, bundle_id: int) -> int: ...

    def list_data_record_index_page(
        self,
        bundle_id: int,
        *,
        query: TraceIndexPageQuery | None = None,
        **kwargs: object,
    ) -> tuple[list[TraceIndexRow], int]: ...

