from functools import lru_cache

from pydantic import PostgresDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import URL, make_url


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    PROJECT_NAME: str = "Fasten API"
    API_V1_STR: str = "/api/v1"
    DATABASE_URL: PostgresDsn
    BACKEND_CORS_ORIGINS: list[str] = []
    DB_ECHO: bool = False
    DATABASE_HOST_OVERRIDE: str | None = None

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def async_postgres(cls, value):
        url = make_url(str(value))
        if url.drivername not in {"postgres", "postgresql", "postgresql+asyncpg"}:
            raise ValueError("DATABASE_URL must use PostgreSQL with asyncpg")
        return url.set(drivername="postgresql+asyncpg").render_as_string(
            hide_password=False
        )

    @field_validator("BACKEND_CORS_ORIGINS")
    @classmethod
    def explicit_origins(cls, value):
        if "*" in value:
            raise ValueError("Use explicit CORS origins")
        return value

    @property
    def database_url(self) -> URL:
        return (
            make_url(str(self.DATABASE_URL)).set(host=self.DATABASE_HOST_OVERRIDE)
            if self.DATABASE_HOST_OVERRIDE
            else make_url(str(self.DATABASE_URL))
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()
