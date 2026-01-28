"""Repository for DerivedParameter operations."""

from sqlmodel import Session, select

from core.shared.persistence.models import DerivedParameter


class DerivedParameterRepository:
    """Repository for DerivedParameter operations."""

    def __init__(self, session: Session):
        self._session = session

    def list_by_dataset(self, dataset_id: int) -> list[DerivedParameter]:
        """List all derived parameters for a dataset."""
        statement = select(DerivedParameter).where(DerivedParameter.dataset_id == dataset_id)
        return list(self._session.exec(statement).all())

    def add(self, param: DerivedParameter) -> DerivedParameter:
        """Add a new derived parameter."""
        self._session.add(param)
        return param

    def list_all(self) -> list[DerivedParameter]:
        """List all derived parameters."""
        statement = select(DerivedParameter).order_by(DerivedParameter.id)
        return list(self._session.exec(statement).all())

    def get(self, id: int) -> DerivedParameter | None:
        """Get derived parameter by ID."""
        return self._session.get(DerivedParameter, id)

    def delete(self, param: DerivedParameter) -> None:
        """Delete a derived parameter."""
        self._session.delete(param)

    def reorder_id(self, old_id: int, new_id: int) -> DerivedParameter:
        """Change derived parameter ID."""
        if self.get(new_id):
            raise ValueError(f"Target ID {new_id} already exists.")

        param = self.get(old_id)
        if not param:
            raise ValueError(f"Source ID {old_id} not found.")

        from sqlmodel import update

        from core.shared.persistence.models import DerivedParameter

        self._session.exec(
            update(DerivedParameter).where(DerivedParameter.id == old_id).values(id=new_id)
        )

        self._session.expire(param)
        return self.get(new_id)
