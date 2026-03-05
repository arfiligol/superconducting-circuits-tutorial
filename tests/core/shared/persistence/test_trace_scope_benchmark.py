"""Large-dataset baseline tests for trace-scope paging queries."""

from __future__ import annotations

from datetime import UTC, datetime
from time import perf_counter

from sqlmodel import Session, SQLModel, create_engine

from core.shared.persistence.models import DataRecord, DatasetRecord
from core.shared.persistence.repositories.data_record_repository import DataRecordRepository
from core.shared.persistence.repositories.query_objects import TraceIndexPageQuery


def _memory_session() -> Session:
    engine = create_engine("sqlite://")
    SQLModel.metadata.create_all(engine)
    return Session(engine)


def _seed_large_dataset(session: Session, *, total: int) -> DatasetRecord:
    dataset = DatasetRecord(name=f"LargeDataset_{total}", source_meta={}, parameters={})
    session.add(dataset)
    session.flush()
    assert dataset.id is not None

    rows = [
        DataRecord(
            dataset_id=dataset.id,
            data_type="y_parameters",
            parameter=f"Y11 [om=(0,), im=({index % 5},)]" if index % 3 == 0 else "Y11",
            representation="imaginary",
            axes=[{"name": "frequency", "unit": "GHz", "values": [5.0, 6.0]}],
            values=[0.01, 0.02],
            created_at=datetime.now(UTC),
        )
        for index in range(total)
    ]
    session.add_all(rows)
    session.commit()
    return dataset


def test_large_trace_scope_query_returns_paged_rows_under_baseline_time() -> None:
    """JTWPA-scale trace metadata queries should stay on paged path."""
    with _memory_session() as session:
        dataset = _seed_large_dataset(session, total=10_000)
        assert dataset.id is not None

        repo = DataRecordRepository(session)
        query = TraceIndexPageQuery(
            search="Y11",
            mode_filter="base",
            sort_by="id",
            descending=False,
            limit=20,
            offset=100,
        )

        started = perf_counter()
        rows, total = repo.list_index_page_by_dataset(dataset.id, query=query)
        elapsed = perf_counter() - started

        # One-third of rows are sideband and excluded by mode_filter="base".
        assert total == 6_666
        assert len(rows) == 20
        # Baseline guardrail: keep metadata paging query within a practical budget.
        assert elapsed < 1.5
