"""Tests for result-bundle persistence helpers."""

from sqlmodel import Session, SQLModel, create_engine

from core.shared.persistence.models import (
    CircuitRecord,
    DataRecord,
    DatasetRecord,
    ResultBundleRecord,
)
from core.shared.persistence.repositories.circuit_repository import CircuitRepository
from core.shared.persistence.repositories.data_record_repository import (
    DataRecordRepository,
)
from core.shared.persistence.repositories.dataset_repository import DatasetRepository
from core.shared.persistence.repositories.result_bundle_repository import (
    ResultBundleRepository,
)


def _memory_session() -> Session:
    engine = create_engine("sqlite://")
    SQLModel.metadata.create_all(engine)
    return Session(engine)


def test_dataset_repository_hides_system_datasets_by_default() -> None:
    with _memory_session() as session:
        repo = DatasetRepository(session)
        repo.add(DatasetRecord(name="Visible", source_meta={"system_hidden": False}, parameters={}))
        repo.add(DatasetRecord(name="Hidden", source_meta={"system_hidden": True}, parameters={}))
        session.commit()

        assert [dataset.name for dataset in repo.list_all()] == ["Visible"]
        assert [dataset.name for dataset in repo.list_all(include_hidden=True)] == [
            "Visible",
            "Hidden",
        ]


def test_result_bundle_repository_finds_cache_bundle_and_lists_member_records() -> None:
    with _memory_session() as session:
        dataset_repo = DatasetRepository(session)
        data_repo = DataRecordRepository(session)
        bundle_repo = ResultBundleRepository(session)

        dataset = dataset_repo.add(
            DatasetRecord(name="Cache", source_meta={"system_hidden": True}, parameters={})
        )
        session.flush()
        assert dataset.id is not None

        bundle = bundle_repo.add(
            ResultBundleRecord(
                dataset_id=dataset.id,
                bundle_type="circuit_simulation",
                role="cache",
                status="completed",
                schema_source_hash="sha256:schema",
                simulation_setup_hash="sha256:setup",
                source_meta={},
                config_snapshot={
                    "freq_range": {
                        "start_ghz": 4.0,
                        "stop_ghz": 5.0,
                        "points": 101,
                    }
                },
                result_payload={
                    "frequencies_ghz": [4.0, 5.0],
                    "s11_real": [0.0, 0.0],
                    "s11_imag": [0.0, 0.0],
                },
            )
        )
        session.flush()
        assert bundle.id is not None

        records = [
            data_repo.add(
                DataRecord(
                    dataset_id=dataset.id,
                    data_type="s_params",
                    parameter="S11",
                    representation="real",
                    axes=[{"name": "frequency", "unit": "GHz", "values": [4.0, 5.0]}],
                    values=[0.0, 0.0],
                )
            ),
            data_repo.add(
                DataRecord(
                    dataset_id=dataset.id,
                    data_type="s_params",
                    parameter="S11",
                    representation="imaginary",
                    axes=[{"name": "frequency", "unit": "GHz", "values": [4.0, 5.0]}],
                    values=[0.0, 0.0],
                )
            ),
        ]
        session.flush()
        bundle_repo.attach_data_records(
            bundle_id=bundle.id,
            data_record_ids=[record.id for record in records if record.id is not None],
        )
        session.commit()

        resolved = bundle_repo.find_simulation_cache(
            dataset_id=dataset.id,
            schema_source_hash="sha256:schema",
            simulation_setup_hash="sha256:setup",
        )

        assert resolved is not None
        assert resolved.id == bundle.id
        assert [
            (record.parameter, record.representation)
            for record in bundle_repo.list_data_records(bundle.id)
        ] == [("S11", "real"), ("S11", "imaginary")]
        assert data_repo.list_all() == []
        assert len(data_repo.list_all(include_hidden=True)) == 2


def test_data_record_repository_index_page_filters_and_sorts() -> None:
    with _memory_session() as session:
        dataset = DatasetRepository(session).add(
            DatasetRecord(name="Dataset A", source_meta={}, parameters={})
        )
        session.flush()
        assert dataset.id is not None

        data_repo = DataRecordRepository(session)
        data_repo.add(
            DataRecord(
                dataset_id=dataset.id,
                data_type="s_params",
                parameter="S11",
                representation="real",
                axes=[],
                values=[],
            )
        )
        data_repo.add(
            DataRecord(
                dataset_id=dataset.id,
                data_type="s_params",
                parameter="S21",
                representation="imaginary",
                axes=[],
                values=[],
            )
        )
        data_repo.add(
            DataRecord(
                dataset_id=dataset.id,
                data_type="y_params",
                parameter="Y11",
                representation="imaginary",
                axes=[],
                values=[],
            )
        )
        session.commit()

        page_rows, total = data_repo.list_index_page_by_dataset(
            dataset.id,
            search="s",
            sort_by="parameter",
            descending=False,
            data_type="s_params",
            limit=1,
            offset=0,
        )
        assert total == 2
        assert len(page_rows) == 1
        assert page_rows[0]["parameter"] == "S11"

        page_rows_2, total_2 = data_repo.list_index_page_by_dataset(
            dataset.id,
            search="s",
            sort_by="parameter",
            descending=False,
            data_type="s_params",
            limit=1,
            offset=1,
        )
        assert total_2 == 2
        assert len(page_rows_2) == 1
        assert page_rows_2[0]["parameter"] == "S21"


def test_circuit_repository_summary_page_supports_search_and_sort() -> None:
    with _memory_session() as session:
        circuit_repo = CircuitRepository(session)
        circuit_repo.add(CircuitRecord(name="Gamma", definition_json="{}"))
        circuit_repo.add(CircuitRecord(name="Alpha", definition_json="{}"))
        circuit_repo.add(CircuitRecord(name="Beta", definition_json="{}"))
        session.commit()

        page_rows, total = circuit_repo.list_summary_page(
            search="a",
            sort_by="name",
            descending=False,
            limit=2,
            offset=0,
        )
        assert total == 3
        assert [row["name"] for row in page_rows] == ["Alpha", "Beta"]
