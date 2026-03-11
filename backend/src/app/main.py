from fastapi import FastAPI

from src.app.api.errors import install_error_handlers
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
    install_error_handlers(app)
    app.include_router(api_router)
    return app


app = create_application()
