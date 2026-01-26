"""Repository for DatasetRecord operations."""

from sqlalchemy import desc
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
        statement = select(DatasetRecord).order_by(
            desc(DatasetRecord.created_at)  # type: ignore[arg-type]
        )
        return list(self._session.exec(statement).all())

    def list_by_tag(self, tag_name: str) -> list[DatasetRecord]:
        """List datasets with a specific tag."""
        statement = (
            select(DatasetRecord)
            .join(DatasetTagLink, DatasetRecord.id == DatasetTagLink.dataset_id)  # type: ignore[arg-type]
            .join(Tag, DatasetTagLink.tag_id == Tag.id)  # type: ignore[arg-type]
            .where(Tag.name == tag_name)
            .order_by(desc(DatasetRecord.created_at))  # type: ignore[arg-type]
        )
        return list(self._session.exec(statement).all())

    def add(self, dataset: DatasetRecord) -> DatasetRecord:
        """Add a new dataset."""
        self._session.add(dataset)
        return dataset

    def delete(self, dataset: DatasetRecord) -> None:
        """Delete a dataset."""
        self._session.delete(dataset)
