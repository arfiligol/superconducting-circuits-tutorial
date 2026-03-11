from fastapi import FastAPI

from src.app.api.router import api_router
from src.app.settings import AppSettings, get_settings


def create_application(settings: AppSettings | None = None) -> FastAPI:
    app_settings = settings or get_settings()
    app = FastAPI(
        title=app_settings.app_name,
        version=app_settings.app_version,
        docs_url="/docs",
        redoc_url="/redoc",
    )
    app.include_router(api_router)
    return app


app = create_application()
