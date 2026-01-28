"""Service for managing DataRecords."""

from typing import cast

from core.analysis.application.dto.data_record_dtos import (
    DataRecordDetailDTO,
    DataRecordSummaryDTO,
)
from core.shared.persistence import get_unit_of_work
from core.shared.persistence.models import DataRecord


class DataRecordManagementService:
    """Service to manage data records."""

    def list_records(self) -> list[DataRecordSummaryDTO]:
        """List all data records."""
        with get_unit_of_work() as uow:
            records = uow.data_records.list_all()
            return [self._to_summary(r) for r in records]

    def get_record(self, id: int) -> DataRecordDetailDTO | None:
        """Get data record details."""
        with get_unit_of_work() as uow:
            record = uow.data_records.get(id)
            return self._to_detail(record) if record else None

    def delete_record(self, id: int) -> bool:
        """Delete a data record."""
        with get_unit_of_work() as uow:
            record = uow.data_records.get(id)
            if not record:
                return False

            uow.data_records.delete(record)
            uow.commit()
            return True

    def auto_reorder(self) -> int:
        """Automatically reorder IDs to be sequential (1..N)."""
        count = 0
        with get_unit_of_work() as uow:
            records = sorted(uow.data_records.list_all(), key=lambda x: x.id)
            for idx, record in enumerate(records, start=1):
                if record.id != idx:
                    try:
                        uow.data_records.reorder_id(record.id, idx)
                        count += 1
                    except ValueError:
                        pass
            uow.commit()
            return count

    def _to_summary(self, record: DataRecord) -> DataRecordSummaryDTO:
        return DataRecordSummaryDTO(
            id=cast(int, record.id),
            dataset_id=record.dataset_id,
            data_type=record.data_type,
            parameter=record.parameter,
            representation=record.representation,
        )

    def _to_detail(self, record: DataRecord) -> DataRecordDetailDTO:
        return DataRecordDetailDTO(
            id=cast(int, record.id),
            dataset_id=record.dataset_id,
            data_type=record.data_type,
            parameter=record.parameter,
            representation=record.representation,
            axes=record.axes,
            values=record.values,
        )
