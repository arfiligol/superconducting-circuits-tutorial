from src.app.domain.audit import AuditRecord


class InMemoryTaskAuditRepository:
    def __init__(self) -> None:
        self._records: list[AuditRecord] = []

    def append(self, record: AuditRecord) -> AuditRecord:
        self._records.append(record)
        return record

    def list_records(self) -> tuple[AuditRecord, ...]:
        return tuple(self._records)

    def list_records_for_resource(
        self,
        *,
        resource_kind: str,
        resource_id: str,
    ) -> tuple[AuditRecord, ...]:
        return tuple(
            record
            for record in self._records
            if record.resource_kind == resource_kind and record.resource_id == resource_id
        )
