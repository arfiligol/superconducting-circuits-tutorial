from functools import lru_cache

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

from src.app.infrastructure.secret_management import validate_secret_management_baseline


class AppSettings(BaseSettings):
    app_name: str = "Superconducting Circuits API"
    app_version: str = "0.1.0"
    environment: str = "development"
    session_secret: SecretStr = SecretStr("change-me-session-secret")
    bootstrap_admin_username: str = "admin"
    bootstrap_admin_password: SecretStr = SecretStr("change-me-bootstrap-password")

    model_config = SettingsConfigDict(
        env_prefix="SC_",
        extra="ignore",
    )


@lru_cache(maxsize=1)
def get_settings() -> AppSettings:
    settings = AppSettings()
    validate_secret_management_baseline(settings)
    return settings
