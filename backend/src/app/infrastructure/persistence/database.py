from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from src.app.infrastructure.persistence.models import RewriteMetadataBase

DEFAULT_DATABASE_PATH = "data/database.db"


def resolve_metadata_database_path(configured_path: str = DEFAULT_DATABASE_PATH) -> Path:
    database_path = Path(configured_path).expanduser()
    if not database_path.is_absolute():
        database_path = (_repo_root() / database_path).resolve()
    database_path.parent.mkdir(parents=True, exist_ok=True)
    return database_path


def build_sqlite_database_url(database_path: Path) -> str:
    return f"sqlite:///{database_path}"


def create_metadata_engine(configured_path: str = DEFAULT_DATABASE_PATH) -> Engine:
    return create_engine(build_sqlite_database_url(resolve_metadata_database_path(configured_path)))


def create_metadata_session_factory(
    configured_path: str = DEFAULT_DATABASE_PATH,
) -> sessionmaker[Session]:
    return sessionmaker(
        bind=create_metadata_engine(configured_path),
        expire_on_commit=False,
    )


def bootstrap_metadata_schema(configured_path: str = DEFAULT_DATABASE_PATH) -> None:
    engine = create_metadata_engine(configured_path)
    RewriteMetadataBase.metadata.create_all(engine)


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[5]
