"""Repository for ResultBundleRecord operations."""

from sqlmodel import Session, select

from core.shared.persistence.models import (
    DataRecord,
    ResultBundleDataLink,
    ResultBundleRecord,
)


class ResultBundleRepository:
    """Repository for ResultBundleRecord operations."""

    def __init__(self, session: Session):
        self._session = session

    def get(self, id: int) -> ResultBundleRecord | None:
        """Get a result bundle by ID."""
        return self._session.get(ResultBundleRecord, id)

    def add(self, bundle: ResultBundleRecord) -> ResultBundleRecord:
        """Add a new result bundle."""
        self._session.add(bundle)
        return bundle

    def list_by_dataset(self, dataset_id: int) -> list[ResultBundleRecord]:
        """List all result bundles under one dataset."""
        statement = (
            select(ResultBundleRecord)
            .where(ResultBundleRecord.dataset_id == dataset_id)
            .order_by(ResultBundleRecord.id)  # type: ignore[arg-type]
        )
        return list(self._session.exec(statement).all())

    def find_simulation_cache(
        self,
        *,
        dataset_id: int,
        schema_source_hash: str,
        simulation_setup_hash: str,
    ) -> ResultBundleRecord | None:
        """Find one completed circuit-simulation cache bundle by formal identity."""
        statement = (
            select(ResultBundleRecord)
            .where(ResultBundleRecord.dataset_id == dataset_id)
            .where(ResultBundleRecord.bundle_type == "circuit_simulation")
            .where(ResultBundleRecord.role == "cache")
            .where(ResultBundleRecord.status == "completed")
            .where(ResultBundleRecord.schema_source_hash == schema_source_hash)
            .where(ResultBundleRecord.simulation_setup_hash == simulation_setup_hash)
            .order_by(ResultBundleRecord.id.desc())  # type: ignore[union-attr]
        )
        return self._session.exec(statement).first()

    def attach_data_records(self, *, bundle_id: int, data_record_ids: list[int]) -> None:
        """Attach existing DataRecord rows to a bundle."""
        for data_record_id in data_record_ids:
            self._session.add(
                ResultBundleDataLink(
                    result_bundle_id=bundle_id,
                    data_record_id=data_record_id,
                )
            )

    def list_data_records(self, bundle_id: int) -> list[DataRecord]:
        """List all DataRecord rows attached to one bundle."""
        statement = (
            select(DataRecord)
            .join(
                ResultBundleDataLink,
                DataRecord.id == ResultBundleDataLink.data_record_id,  # type: ignore[arg-type]
            )
            .where(ResultBundleDataLink.result_bundle_id == bundle_id)
            .order_by(DataRecord.id)  # type: ignore[arg-type]
        )
        return list(self._session.exec(statement).all())

    def list_data_record_index(self, bundle_id: int) -> list[dict[str, str | int]]:
        """List lightweight metadata for bundle-linked DataRecord rows only."""
        statement = (
            select(
                DataRecord.id,
                DataRecord.data_type,
                DataRecord.parameter,
                DataRecord.representation,
            )
            .join(
                ResultBundleDataLink,
                DataRecord.id == ResultBundleDataLink.data_record_id,  # type: ignore[arg-type]
            )
            .where(ResultBundleDataLink.result_bundle_id == bundle_id)
            .order_by(DataRecord.id)  # type: ignore[arg-type]
        )
        rows = self._session.exec(statement).all()
        return [
            {
                "id": int(record_id),
                "data_type": str(data_type),
                "parameter": str(parameter),
                "representation": str(representation),
            }
            for record_id, data_type, parameter, representation in rows
            if record_id is not None
        ]
