"""Repository contracts used by page/application orchestration layers."""

from __future__ import annotations

from typing import Any, Protocol, TypedDict, runtime_checkable

from core.shared.persistence.repositories.query_objects import TraceIndexPageQuery

TraceIndexRow = dict[str, str | int]


class AnalysisRunSummary(TypedDict):
    """Primitive-only summary row for one analysis run."""

    analysis_run_id: int
    design_id: int
    analysis_id: str
    analysis_label: str
    status: str


class TraceBatchSnapshot(TypedDict):
    """Canonical trace-batch snapshot DTO for lineage/provenance lookups."""

    id: int
    design_id: int
    source_kind: str
    stage_kind: str
    status: str
    parent_batch_id: int | None
    setup_kind: str | None
    setup_version: str | None
    provenance_payload: dict[str, Any]
    setup_payload: dict[str, Any]
    summary_payload: dict[str, Any]


class ResultBundleAnalysisRunSummary(TypedDict):
    """Legacy primitive-only summary row for one characterization bundle."""

    bundle_id: int
    dataset_id: int
    analysis_id: str
    analysis_label: str
    status: str


class ResultBundleSnapshot(TypedDict):
    """Legacy snapshot DTO for result-bundle provenance lookups."""

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
class TraceCharacterizationContract(Protocol):
    """Minimal Trace repository API required by trace-first characterization flows."""

    def count_by_design(self, design_id: int) -> int: ...

    def list_distinct_index_for_profile(self, design_id: int) -> list[dict[str, str]]: ...

    def list_index_page_by_design(
        self,
        design_id: int,
        *,
        query: TraceIndexPageQuery | None = None,
        **kwargs: object,
    ) -> tuple[list[TraceIndexRow], int]: ...


@runtime_checkable
class TraceBatchCharacterizationContract(Protocol):
    """Minimal TraceBatch repository API required by trace-selection flows."""

    def count_traces(self, batch_id: int) -> int: ...

    def list_trace_index_page(
        self,
        batch_id: int,
        *,
        query: TraceIndexPageQuery | None = None,
        **kwargs: object,
    ) -> tuple[list[TraceIndexRow], int]: ...


@runtime_checkable
class TraceBatchDesignSummaryContract(Protocol):
    """TraceBatch summary API used by design-scoped UI summaries."""

    def count_by_design(
        self,
        design_id: int,
        *,
        bundle_type: str | None = None,
        role: str | None = None,
        include_cache: bool = True,
    ) -> int: ...

    def list_analysis_run_summaries_by_design(
        self,
        design_id: int,
    ) -> list[AnalysisRunSummary]: ...


@runtime_checkable
class TraceBatchSnapshotContract(Protocol):
    """TraceBatch provenance lookup API that returns canonical DTO snapshots only."""

    def get_trace_batch_snapshot(self, id: int) -> TraceBatchSnapshot | None: ...


@runtime_checkable
class DataRecordCharacterizationContract(Protocol):
    """Legacy DataRecord repository API required by characterization/runtime flows."""

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
    """Legacy ResultBundle repository API required by characterization/runtime flows."""

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
    """Legacy ResultBundle summary API used by dataset-scoped UI summaries."""

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
    """Legacy ResultBundle provenance lookup API that returns DTO snapshots only."""

    def get_snapshot(self, id: int) -> ResultBundleSnapshot | None: ...
