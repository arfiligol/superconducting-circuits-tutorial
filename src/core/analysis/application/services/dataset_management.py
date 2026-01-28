"""Service for managing datasets (List, Get, Delete)."""

from typing import cast

from core.analysis.application.dto.dataset_dtos import DatasetDetailDTO, DatasetSummaryDTO
from core.shared.persistence import get_unit_of_work
from core.shared.persistence.models import DatasetRecord


class DatasetManagementService:
    """Service to manage datasets using Clean Architecture."""

    def list_datasets(self) -> list[DatasetSummaryDTO]:
        """List all datasets with summary info."""
        with get_unit_of_work() as uow:
            records = uow.datasets.list_all()
            return [self._to_summary(r) for r in records]

    def get_dataset(self, identifier: str) -> DatasetDetailDTO | None:
        """
        Get dataset details by ID (int as str) or Name (str).

        Args:
            identifier: ID or Name of the dataset.

        Returns:
            DatasetDetailDTO if found, None otherwise.
        """
        with get_unit_of_work() as uow:
            record = self._find_record(uow, identifier)
            if not record:
                return None

            # Count data records explicitly if needed, or rely on relationship lazy load
            # Here we assume relationship is available.
            # Note: In async/detached scenarios, lazy loading might fail.
            # But SqliteUnitOfWork keeps session open in context.
            record_count = len(record.data_records)

            return self._to_detail(record, record_count)

    def delete_dataset(self, identifier: str) -> bool:
        """
        Delete a dataset by ID or Name.

        Returns:
            True if deleted, False if not found.
        """
        with get_unit_of_work() as uow:
            record = self._find_record(uow, identifier)
            if not record:
                return False

            uow.datasets.delete(record)
            uow.commit()
            return True

    def auto_reorder(self) -> int:
        """
        Automatically reorder IDs to be sequential (1..N).
        Sorts by current ID to preserve relative order.
        """
        count = 0
        with get_unit_of_work() as uow:
            # Fetch all and sort by ID to safely compact
            records = sorted(uow.datasets.list_all(), key=lambda x: x.id)

            for idx, record in enumerate(records, start=1):
                if record.id != idx:
                    # We can assume safe to reorder because we are moving to
                    # 'idx', which is always <= record.id in a sorted list of unique positive ints,
                    # and 'idx' is free because we processed all previous IDs (1..idx-1).
                    try:
                        uow.datasets.reorder_id(record.id, idx)
                        count += 1
                        # Need to update the session state if we continue?
                        # reorder_id commits? No, repo usually doesn't commit.
                        # Service auto_reorder should commit at end or per step?
                        # Since reorder_id in repo does flush/delete, we should probably commit
                        # to safeguard against constraint violation if we accumulate too much?
                        # But commit breaks transaction atomicity for the whole batch.
                        # Repo reorder_id uses "flush", so it hits DB.
                        # If we process sequentially:
                        # 1. 5 -> 1. New 1 created. Old 5 deleted.
                        # 2. 6 -> 2. New 2 created. Old 6 deleted.
                        # This should be fine in one transaction.
                    except ValueError:
                        # Should not happen in sequential compaction
                        pass

            uow.commit()
            return count

    def _find_record(self, uow, identifier: str) -> DatasetRecord | None:
        """Helper to find record by ID or Name."""
        if identifier.isdigit():
            return uow.datasets.get(int(identifier))
        return uow.datasets.get_by_name(identifier)

    def _to_summary(self, record: DatasetRecord) -> DatasetSummaryDTO:
        """Convert Model to Summary DTO."""
        tags = [t.name for t in record.tags]
        origin = record.source_meta.get("origin") if record.source_meta else None

        return DatasetSummaryDTO(
            id=cast(int, record.id),
            name=record.name,
            created_at=record.created_at,
            tags=tags,
            origin=cast(str | None, origin),
        )

    def _to_detail(self, record: DatasetRecord, record_count: int) -> DatasetDetailDTO:
        """Convert Model to Detail DTO."""
        tags = [t.name for t in record.tags]
        meta = record.source_meta or {}
        origin = meta.get("origin")
        raw_files = meta.get("raw_files", [])

        return DatasetDetailDTO(
            id=cast(int, record.id),
            name=record.name,
            created_at=record.created_at,
            origin=cast(str | None, origin),
            source_files=cast(list[str], raw_files),
            tags=tags,
            parameters=record.parameters or {},
            data_records_count=record_count,
        )
