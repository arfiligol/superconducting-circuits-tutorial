"""Repository for Tag operations."""

from sqlmodel import Session, select

from core.shared.persistence.models import Tag


class TagRepository:
    """Repository for Tag operations."""

    def __init__(self, session: Session):
        self._session = session

    def get_or_create(self, name: str) -> Tag:
        """Get existing tag or create new one."""
        statement = select(Tag).where(Tag.name == name)
        tag = self._session.exec(statement).first()
        if tag is None:
            tag = Tag(name=name)
            self._session.add(tag)
        return tag

    def list_all(self) -> list[Tag]:
        """List all tags."""
        statement = select(Tag).order_by(Tag.name)
        return list(self._session.exec(statement).all())
