"""Tests for Characterization trace-scope query service."""

from __future__ import annotations

from dataclasses import dataclass

from app.services.characterization_trace_scope import (
    count_scope_trace_records,
    list_scope_compatible_trace_index_page,
)


@dataclass
class _FakeDataRecordsRepo:
    count_value: int = 0
    page_rows: list[dict[str, str | int]] | None = None
    page_total: int = 0
    counted_dataset_id: int | None = None
    page_dataset_id: int | None = None
    last_query: object | None = None

    def count_by_dataset(self, dataset_id: int) -> int:
        self.counted_dataset_id = dataset_id
        return self.count_value

    def list_index_page_by_dataset(self, dataset_id: int, *, query: object) -> tuple[list, int]:
        self.page_dataset_id = dataset_id
        self.last_query = query
        return (self.page_rows or []), self.page_total


@dataclass
class _FakeResultBundlesRepo:
    count_value: int = 0
    page_rows: list[dict[str, str | int]] | None = None
    page_total: int = 0
    counted_bundle_id: int | None = None
    page_bundle_id: int | None = None
    last_query: object | None = None

    def count_data_records(self, bundle_id: int) -> int:
        self.counted_bundle_id = bundle_id
        return self.count_value

    def list_data_record_index_page(self, bundle_id: int, *, query: object) -> tuple[list, int]:
        self.page_bundle_id = bundle_id
        self.last_query = query
        return (self.page_rows or []), self.page_total


@dataclass
class _FakeUow:
    data_records: _FakeDataRecordsRepo
    result_bundles: _FakeResultBundlesRepo


def test_count_scope_trace_records_uses_dataset_repo_when_scope_is_all_dataset() -> None:
    data_records = _FakeDataRecordsRepo(count_value=42)
    bundles = _FakeResultBundlesRepo(count_value=7)
    uow = _FakeUow(data_records=data_records, result_bundles=bundles)

    total = count_scope_trace_records(uow=uow, dataset_id=12, selected_bundle_id=None)

    assert total == 42
    assert data_records.counted_dataset_id == 12
    assert bundles.counted_bundle_id is None


def test_count_scope_trace_records_uses_bundle_repo_when_bundle_is_selected() -> None:
    data_records = _FakeDataRecordsRepo(count_value=42)
    bundles = _FakeResultBundlesRepo(count_value=7)
    uow = _FakeUow(data_records=data_records, result_bundles=bundles)

    total = count_scope_trace_records(uow=uow, dataset_id=12, selected_bundle_id=99)

    assert total == 7
    assert bundles.counted_bundle_id == 99
    assert data_records.counted_dataset_id is None


def test_list_scope_compatible_trace_index_page_builds_normalized_query() -> None:
    data_records = _FakeDataRecordsRepo(
        page_rows=[{"id": 1, "parameter": "Y11", "representation": "imaginary"}],
        page_total=1,
    )
    bundles = _FakeResultBundlesRepo()
    uow = _FakeUow(data_records=data_records, result_bundles=bundles)

    rows, total = list_scope_compatible_trace_index_page(
        uow=uow,
        dataset_id=5,
        selected_bundle_id=None,
        analysis_requires={
            "data_type": "y_params",
            "parameter": "Y11 [om=(0,)]",
            "representation": "Imaginary",
        },
        mode_filter="invalid",
        limit=10,
        offset=20,
    )

    assert rows == [{"id": 1, "parameter": "Y11", "representation": "imaginary"}]
    assert total == 1
    query = data_records.last_query
    assert query is not None
    assert query.data_types == ("y_parameters", "y_params")
    assert query.parameters == ("Y11",)
    assert query.representation == "imaginary"
    assert query.mode_filter == "all"
    assert query.limit == 10
    assert query.offset == 20
