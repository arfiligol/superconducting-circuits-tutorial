"""Repository contracts used by page/application orchestration layers."""

from __future__ import annotations

from typing import Any, Protocol, TypedDict, runtime_checkable

from core.shared.persistence.repositories.query_objects import TraceIndexPageQuery

TraceIndexRow = dict[str, str | int]


class ResultBundleAnalysisRunSummary(TypedDict):
    """Primitive-only summary row for one characterization analysis run bundle."""

    bundle_id: int
    dataset_id: int
    analysis_id: str
    analysis_label: str
    status: str


class ResultBundleSnapshot(TypedDict):
    """Primitive snapshot DTO for result-bundle provenance lookups."""

    id: int
    dataset_id: int
    bundle_type: str
    role: str
    status: str
    schema_source_hash: str | None
    simulation_setup_hash: str | None
    source_meta: dict[str, Any]
    config_snapshot: dict[str, Any]
    result_payload: dict[str, Any]


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


@runtime_checkable
class ResultBundleDatasetSummaryContract(Protocol):
    """ResultBundle summary API used by dataset-scoped UI summaries."""

    def count_by_dataset(
        self,
        dataset_id: int,
        *,
        bundle_type: str | None = None,
        role: str | None = None,
        include_cache: bool = True,
    ) -> int: ...

    def list_analysis_run_summaries_by_dataset(
        self,
        dataset_id: int,
    ) -> list[ResultBundleAnalysisRunSummary]: ...


@runtime_checkable
class ResultBundleSnapshotContract(Protocol):
    """ResultBundle provenance lookup API that returns DTO snapshots only."""

    def get_snapshot(self, id: int) -> ResultBundleSnapshot | None: ...
