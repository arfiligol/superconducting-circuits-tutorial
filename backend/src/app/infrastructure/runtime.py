from src.app.services.health_service import HealthService
from src.app.settings import get_settings


def get_health_service() -> HealthService:
    settings = get_settings()
    return HealthService(
        app_name=settings.app_name,
        environment=settings.environment,
    )
