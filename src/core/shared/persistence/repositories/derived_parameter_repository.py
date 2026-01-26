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
