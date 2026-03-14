from functools import lru_cache

from src.app.infrastructure.persistence import (
    SqliteRewriteStorageMetadataRepository,
    SqliteRewriteTaskSnapshotRepository,
    bootstrap_metadata_schema,
    create_metadata_session_factory,
)
from src.app.infrastructure.rewrite_app_state_repository import InMemoryRewriteAppStateRepository
from src.app.infrastructure.rewrite_catalog_repository import InMemoryRewriteCatalogRepository
from src.app.infrastructure.rewrite_execution_runtime import RewriteExecutionRuntime
from src.app.infrastructure.rewrite_task_repository import PersistedRewriteTaskRepository
from src.app.services.circuit_definition_service import CircuitDefinitionService
from src.app.services.dataset_service import DatasetService
from src.app.services.health_service import HealthService
from src.app.services.session_service import SessionService
from src.app.services.task_service import TaskService
from src.app.settings import get_settings


@lru_cache(maxsize=1)
def get_rewrite_catalog_repository() -> InMemoryRewriteCatalogRepository:
    return InMemoryRewriteCatalogRepository()


@lru_cache(maxsize=1)
def get_rewrite_app_state_repository() -> InMemoryRewriteAppStateRepository:
    return InMemoryRewriteAppStateRepository(
        include_task_scaffold=False,
    )


@lru_cache(maxsize=1)
def get_storage_metadata_repository() -> SqliteRewriteStorageMetadataRepository:
    settings = get_settings()
    bootstrap_metadata_schema(settings.database_path)
    return SqliteRewriteStorageMetadataRepository(
        create_metadata_session_factory(settings.database_path)
    )


@lru_cache(maxsize=1)
def get_task_snapshot_repository() -> SqliteRewriteTaskSnapshotRepository:
    settings = get_settings()
    bootstrap_metadata_schema(settings.database_path)
    return SqliteRewriteTaskSnapshotRepository(
        create_metadata_session_factory(settings.database_path)
    )


@lru_cache(maxsize=1)
def get_rewrite_task_repository() -> PersistedRewriteTaskRepository:
    return PersistedRewriteTaskRepository(
        task_snapshot_repository=get_task_snapshot_repository(),
        storage_metadata_repository=get_storage_metadata_repository(),
    )


def get_health_service() -> HealthService:
    settings = get_settings()
    return HealthService(
        app_name=settings.app_name,
        environment=settings.environment,
    )


@lru_cache(maxsize=1)
def get_dataset_service() -> DatasetService:
    return DatasetService(
        repository=get_rewrite_catalog_repository(),
        session_repository=get_rewrite_app_state_repository(),
    )


@lru_cache(maxsize=1)
def get_circuit_definition_service() -> CircuitDefinitionService:
    return CircuitDefinitionService(repository=get_rewrite_catalog_repository())


@lru_cache(maxsize=1)
def get_session_service() -> SessionService:
    return SessionService(
        repository=get_rewrite_app_state_repository(),
        dataset_repository=get_rewrite_catalog_repository(),
    )


@lru_cache(maxsize=1)
def get_task_service() -> TaskService:
    return TaskService(
        repository=get_rewrite_task_repository(),
        session_repository=get_rewrite_app_state_repository(),
        dataset_repository=get_rewrite_catalog_repository(),
        circuit_definition_repository=get_rewrite_catalog_repository(),
    )


@lru_cache(maxsize=1)
def get_task_execution_runtime() -> RewriteExecutionRuntime:
    return RewriteExecutionRuntime(
        task_service=get_task_service(),
        task_repository=get_rewrite_task_repository(),
    )


def reset_runtime_state() -> None:
    get_settings.cache_clear()
    get_rewrite_catalog_repository.cache_clear()
    get_rewrite_app_state_repository.cache_clear()
    get_storage_metadata_repository.cache_clear()
    get_task_snapshot_repository.cache_clear()
    get_rewrite_task_repository.cache_clear()
    get_dataset_service.cache_clear()
    get_circuit_definition_service.cache_clear()
    get_session_service.cache_clear()
    get_task_service.cache_clear()
    get_task_execution_runtime.cache_clear()
