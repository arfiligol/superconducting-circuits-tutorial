from functools import lru_cache

from src.app.infrastructure.rewrite_app_state_repository import InMemoryRewriteAppStateRepository
from src.app.infrastructure.rewrite_catalog_repository import InMemoryRewriteCatalogRepository
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
    return InMemoryRewriteAppStateRepository()


def get_health_service() -> HealthService:
    settings = get_settings()
    return HealthService(
        app_name=settings.app_name,
        environment=settings.environment,
    )


@lru_cache(maxsize=1)
def get_dataset_service() -> DatasetService:
    return DatasetService(repository=get_rewrite_catalog_repository())


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
        repository=get_rewrite_app_state_repository(),
        session_repository=get_rewrite_app_state_repository(),
        dataset_repository=get_rewrite_catalog_repository(),
        circuit_definition_repository=get_rewrite_catalog_repository(),
    )


def reset_runtime_state() -> None:
    get_settings.cache_clear()
    get_rewrite_catalog_repository.cache_clear()
    get_rewrite_app_state_repository.cache_clear()
    get_dataset_service.cache_clear()
    get_circuit_definition_service.cache_clear()
    get_session_service.cache_clear()
    get_task_service.cache_clear()
