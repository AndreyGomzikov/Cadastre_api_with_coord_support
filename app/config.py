from pydantic_settings import BaseSettings, SettingsConfigDict

from app.constants import (
    DEFAULT_DATABASE_URL,
    DEFAULT_EXTERNAL_SERVICE_URL,
    DEFAULT_EXTERNAL_TIMEOUT_SECONDS,
)


class Settings(BaseSettings):
    database_url: str = DEFAULT_DATABASE_URL
    external_service_url: str = DEFAULT_EXTERNAL_SERVICE_URL
    external_timeout_seconds: float = DEFAULT_EXTERNAL_TIMEOUT_SECONDS

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
