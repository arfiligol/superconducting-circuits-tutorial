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

    def list_all(self) -> list[DataRecord]:
        """List all data records."""
        statement = select(DataRecord).order_by(DataRecord.id)
        return list(self._session.exec(statement).all())

    def delete(self, record: DataRecord) -> None:
        """Delete a data record."""
        self._session.delete(record)

    def reorder_id(self, old_id: int, new_id: int) -> DataRecord:
        """Change data record ID."""
        if self.get(new_id):
            raise ValueError(f"Target ID {new_id} already exists.")

        record = self.get(old_id)
        if not record:
            raise ValueError(f"Source ID {old_id} not found.")

        # Since it's a leaf node, we can likely just update the ID directly
        # But SQLModel objects might track PK identity.
        # Direct SQL update is safer to avoid session confusion.
        from sqlmodel import update

        from core.shared.persistence.models import DataRecord

        self._session.exec(update(DataRecord).where(DataRecord.id == old_id).values(id=new_id))

        # Return new object
        # We need to refresh or get new one. Old object is stale.
        # But wait, we need to return valid object.
        self._session.expire(record)  # Expire old one
        return self.get(new_id)  # Get new one
