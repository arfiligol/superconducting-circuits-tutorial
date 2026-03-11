from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    app_name: str = "Superconducting Circuits API"
    app_version: str = "0.1.0"
    environment: str = "development"

    model_config = SettingsConfigDict(
        env_prefix="SC_",
        extra="ignore",
    )


@lru_cache(maxsize=1)
def get_settings() -> AppSettings:
    return AppSettings()
