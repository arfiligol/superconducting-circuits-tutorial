"""Repository for DatasetRecord operations."""

from sqlmodel import Session, select

from core.shared.persistence.models import DatasetRecord, DatasetTagLink, Tag


class DatasetRepository:
    """Repository for DatasetRecord operations."""

    def __init__(self, session: Session):
        self._session = session

    def get(self, id: int) -> DatasetRecord | None:
        """Get dataset by ID."""
        return self._session.get(DatasetRecord, id)

    def get_by_name(self, name: str) -> DatasetRecord | None:
        """Get dataset by unique name."""
        statement = select(DatasetRecord).where(DatasetRecord.name == name)
        return self._session.exec(statement).first()

    def list_all(self) -> list[DatasetRecord]:
        """List all datasets."""
        statement = select(DatasetRecord).order_by(DatasetRecord.id)
        return list(self._session.exec(statement).all())

    def list_by_tag(self, tag_name: str) -> list[DatasetRecord]:
        """List datasets with a specific tag."""
        statement = (
            select(DatasetRecord)
            .join(DatasetTagLink, DatasetRecord.id == DatasetTagLink.dataset_id)  # type: ignore[arg-type]
            .join(Tag, DatasetTagLink.tag_id == Tag.id)  # type: ignore[arg-type]
            .where(Tag.name == tag_name)
            .order_by(DatasetRecord.id)  # type: ignore[arg-type]
        )
        return list(self._session.exec(statement).all())

    def add(self, dataset: DatasetRecord) -> DatasetRecord:
        """Add a new dataset."""
        self._session.add(dataset)
        return dataset

    def delete(self, dataset: DatasetRecord) -> None:
        """Delete a dataset."""
        self._session.delete(dataset)

    def reorder_id(self, old_id: int, new_id: int) -> DatasetRecord:
        """Change dataset ID and update all dependencies."""
        # 1. Check existence
        if self.get(new_id):
            raise ValueError(f"Target ID {new_id} already exists.")

        dataset = self.get(old_id)
        if not dataset:
            raise ValueError(f"Source ID {old_id} not found.")

        # 2. Create new record with specific ID AND TEMP NAME
        # Name is unique, so we must use a temp name until old one is deleted
        temp_name = f"{dataset.name}_TEMP_{new_id}"

        new_dataset = DatasetRecord(
            id=new_id,
            name=temp_name,
            source_meta=dataset.source_meta,
            parameters=dataset.parameters,
            created_at=dataset.created_at,
        )
        self._session.add(new_dataset)
        self._session.flush()  # Ensure new ID is available

        # 3. Update dependencies (DataRecord)
        # We need to import models here or rely on relationship names if using ORM,
        # but raw update is cleaner for batch updates.
        from sqlmodel import update

        from core.shared.persistence.models import DataRecord, DatasetTagLink, DerivedParameter

        self._session.exec(
            update(DataRecord).where(DataRecord.dataset_id == old_id).values(dataset_id=new_id)
        )

        # 4. Update dependencies (DerivedParameter)
        self._session.exec(
            update(DerivedParameter)
            .where(DerivedParameter.dataset_id == old_id)
            .values(dataset_id=new_id)
        )

        # 5. Update dependencies (DatasetTagLink)
        self._session.exec(
            update(DatasetTagLink)
            .where(DatasetTagLink.dataset_id == old_id)
            .values(dataset_id=new_id)
        )

        # 6. Delete old record
        original_name = dataset.name
        self._session.delete(dataset)
        self._session.flush()  # Ensure deletion happens before rename

        # 7. Restore original name
        new_dataset.name = original_name
        self._session.add(new_dataset)
        self._session.flush()

        return new_dataset
