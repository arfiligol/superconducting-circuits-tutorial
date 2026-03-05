"""Repository contract tests for page-orchestration critical APIs."""

from sqlmodel import Session, SQLModel, create_engine

from core.shared.persistence.models import DatasetRecord
from core.shared.persistence.repositories import (
    DataRecordCharacterizationContract,
    DataRecordRepository,
    ResultBundleCharacterizationContract,
    ResultBundleDatasetSummaryContract,
    ResultBundleRepository,
)


def _memory_session() -> Session:
    engine = create_engine("sqlite://")
    SQLModel.metadata.create_all(engine)
    return Session(engine)


def test_data_record_repository_satisfies_characterization_contract() -> None:
    with _memory_session() as session:
        dataset = DatasetRecord(name="Contract Dataset", source_meta={}, parameters={})
        session.add(dataset)
        session.commit()
        session.refresh(dataset)
        assert dataset.id is not None

        repo = DataRecordRepository(session)

        assert isinstance(repo, DataRecordCharacterizationContract)
        assert repo.count_by_dataset(dataset.id) == 0
        assert repo.list_distinct_index_for_profile(dataset.id) == []

        rows, total = repo.list_index_page_by_dataset(dataset.id)
        assert rows == []
        assert total == 0


def test_result_bundle_repository_satisfies_characterization_contract() -> None:
    with _memory_session() as session:
        repo = ResultBundleRepository(session)
        assert isinstance(repo, ResultBundleCharacterizationContract)
        assert repo.count_data_records(1) == 0

        rows, total = repo.list_data_record_index_page(1)
        assert rows == []
        assert total == 0


def test_result_bundle_repository_satisfies_dataset_summary_contract() -> None:
    with _memory_session() as session:
        dataset = DatasetRecord(name="Summary Contract Dataset", source_meta={}, parameters={})
        session.add(dataset)
        session.commit()
        session.refresh(dataset)
        assert dataset.id is not None

        repo = ResultBundleRepository(session)
        assert isinstance(repo, ResultBundleDatasetSummaryContract)
        assert repo.count_by_dataset(dataset.id) == 0
