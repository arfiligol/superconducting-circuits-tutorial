"""Database engine and session management."""

from functools import lru_cache
from pathlib import Path

from sqlmodel import Session, create_engine

# Database file location
DATABASE_PATH = Path(__file__).parent.parent.parent.parent.parent / "data" / "database.db"


@lru_cache
def get_engine():
    """Get the SQLite engine (singleton)."""
    # Ensure parent directory exists
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    return create_engine(f"sqlite:///{DATABASE_PATH}", echo=False)


def get_session() -> Session:
    """Create a new database session."""
    return Session(get_engine())


def init_db() -> None:
    """Initialize the database (create tables if not exist)."""
    from sqlmodel import SQLModel

    from core.shared.persistence.models import (  # noqa: F401 - Import for side effects
        DataRecord,
        DatasetRecord,
        DatasetTagLink,
        DerivedParameter,
        ParameterDesignation,
        ResultBundleDataLink,
        ResultBundleRecord,
        Tag,
    )

    SQLModel.metadata.create_all(get_engine())
