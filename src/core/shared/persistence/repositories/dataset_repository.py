"""Repository for DatasetRecord operations."""

from datetime import datetime
from typing import Any

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

    @staticmethod
    def _is_hidden(dataset: DatasetRecord) -> bool:
        """Return whether this dataset should stay hidden from normal listings."""
        return bool(dataset.source_meta.get("system_hidden"))

    def list_all(self, *, include_hidden: bool = False) -> list[DatasetRecord]:
        """List datasets, excluding system-hidden containers by default."""
        statement = select(DatasetRecord).order_by(DatasetRecord.id)  # type: ignore[arg-type]
        records = list(self._session.exec(statement).all())
        if include_hidden:
            return records
        return [record for record in records if not self._is_hidden(record)]

    def list_summary_page(
        self,
        *,
        search: str = "",
        sort_by: str = "id",
        descending: bool = False,
        limit: int = 20,
        offset: int = 0,
        include_hidden: bool = False,
    ) -> tuple[list[dict[str, int | str | datetime]], int]:
        """List one page of dataset summaries for UI tables/cards."""
        records = self.list_all(include_hidden=include_hidden)

        search_text = search.strip().lower()
        if search_text:
            records = [record for record in records if search_text in record.name.lower()]

        if sort_by == "name":
            records.sort(key=lambda record: record.name.lower(), reverse=descending)
        elif sort_by == "created_at":
            records.sort(key=lambda record: record.created_at, reverse=descending)
        else:
            records.sort(key=lambda record: int(record.id or 0), reverse=descending)

        total = len(records)
        page_rows = records[offset : offset + max(1, limit)]
        return (
            [
                {
                    "id": int(record.id or 0),
                    "name": record.name,
                    "created_at": record.created_at,
                }
                for record in page_rows
            ],
            total,
        )

    def list_by_tag(self, tag_name: str, *, include_hidden: bool = False) -> list[DatasetRecord]:
        """List datasets with a specific tag."""
        statement = (
            select(DatasetRecord)
            .join(DatasetTagLink, DatasetRecord.id == DatasetTagLink.dataset_id)  # type: ignore[arg-type]
            .join(Tag, DatasetTagLink.tag_id == Tag.id)  # type: ignore[arg-type]
            .where(Tag.name == tag_name)
            .order_by(DatasetRecord.id)  # type: ignore[arg-type]
        )
        records = list(self._session.exec(statement).all())
        if include_hidden:
            return records
        return [record for record in records if not self._is_hidden(record)]

    def add(self, dataset: DatasetRecord) -> DatasetRecord:
        """Add a new dataset."""
        self._session.add(dataset)
        return dataset

    def update_source_meta(self, dataset_id: int, source_meta: dict[str, Any]) -> DatasetRecord:
        """Replace one dataset's source_meta payload."""
        dataset = self.get(dataset_id)
        if dataset is None:
            raise ValueError(f"Dataset ID {dataset_id} not found.")
        dataset.source_meta = dict(source_meta)
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

        from core.shared.persistence.models import (
            DataRecord,
            DatasetTagLink,
            DerivedParameter,
            ResultBundleRecord,
        )

        self._session.exec(
            update(DataRecord)
            .where(DataRecord.dataset_id == old_id)  # type: ignore[arg-type]
            .values(dataset_id=new_id)
        )

        # 4. Update dependencies (DerivedParameter)
        self._session.exec(
            update(DerivedParameter)
            .where(DerivedParameter.dataset_id == old_id)  # type: ignore[arg-type]
            .values(dataset_id=new_id)
        )

        # 5. Update dependencies (ResultBundleRecord)
        self._session.exec(
            update(ResultBundleRecord)
            .where(ResultBundleRecord.dataset_id == old_id)  # type: ignore[arg-type]
            .values(dataset_id=new_id)
        )

        # 6. Update dependencies (DatasetTagLink)
        self._session.exec(
            update(DatasetTagLink)
            .where(DatasetTagLink.dataset_id == old_id)  # type: ignore[arg-type]
            .values(dataset_id=new_id)
        )

        # 7. Delete old record
        original_name = dataset.name
        self._session.delete(dataset)
        self._session.flush()  # Ensure deletion happens before rename

        # 8. Restore original name
        new_dataset.name = original_name
        self._session.add(new_dataset)
        self._session.flush()

        return new_dataset
