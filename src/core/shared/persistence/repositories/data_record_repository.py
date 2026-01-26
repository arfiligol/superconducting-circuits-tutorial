"""Repository for DataRecord operations."""

from sqlmodel import Session, select

from core.shared.persistence.models import DataRecord


class DataRecordRepository:
    """Repository for DataRecord operations."""

    def __init__(self, session: Session):
        self._session = session

    def get(self, id: int) -> DataRecord | None:
        """Get data record by ID."""
        return self._session.get(DataRecord, id)

    def list_by_dataset(self, dataset_id: int) -> list[DataRecord]:
        """List all data records for a dataset."""
        statement = select(DataRecord).where(DataRecord.dataset_id == dataset_id)
        return list(self._session.exec(statement).all())

    def add(self, record: DataRecord) -> DataRecord:
        """Add a new data record."""
        self._session.add(record)
        return record
