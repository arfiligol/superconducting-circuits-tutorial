"""Repository for managing CircuitRecord instances."""

from sqlmodel import Session, select

from core.shared.persistence.models import CircuitRecord


class CircuitRepository:
    """Repository for managing circuit definitions in the database."""

    def __init__(self, session: Session):
        self._session = session

    def add(self, circuit: CircuitRecord) -> CircuitRecord:
        """Add a new CircuitRecord to the database."""
        self._session.add(circuit)
        # Flush is implicitly called by the UOW on commit, but you can flush here if needed
        return circuit

    def get(self, record_id: int) -> CircuitRecord | None:
        """Get a CircuitRecord by its ID."""
        return self._session.get(CircuitRecord, record_id)

    def get_by_name(self, name: str) -> CircuitRecord | None:
        """Get a CircuitRecord by its exact name."""
        stmt = select(CircuitRecord).where(CircuitRecord.name == name)
        return self._session.exec(stmt).first()

    def list_all(self) -> list[CircuitRecord]:
        """List all CircuitRecords, ordered by name."""
        stmt = select(CircuitRecord).order_by(CircuitRecord.name)
        return list(self._session.exec(stmt).all())

    def update(self, circuit: CircuitRecord) -> CircuitRecord:
        """Update an existing CircuitRecord."""
        self._session.add(circuit)
        return circuit

    def delete(self, record_id: int) -> bool:
        """Delete a CircuitRecord by its ID."""
        record = self.get(record_id)
        if record:
            self._session.delete(record)
            return True
        return False
