"""Persistence layer for SQLite database access."""

from core.shared.persistence.database import DATABASE_PATH, get_engine, get_session
from core.shared.persistence.models import (
    DataRecord,
    DatasetRecord,
    DatasetTagLink,
    DerivedParameter,
    DeviceType,
    Tag,
)
from core.shared.persistence.unit_of_work import SqliteUnitOfWork, get_unit_of_work

__all__ = [  # noqa: RUF022
    # Database
    "DATABASE_PATH",
    "get_engine",
    "get_session",
    # Models
    "DataRecord",
    "DatasetRecord",
    "DatasetTagLink",
    "DerivedParameter",
    "DeviceType",
    "Tag",
    # Unit of Work
    "SqliteUnitOfWork",
    "get_unit_of_work",
]
