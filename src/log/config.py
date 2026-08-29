from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class LoggingConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    LOG_LEVEL: str = "INFO"
    LOG_REQUEST_ID_HEADER: str = "X-Request-ID"
    LOG_PROCESS_TIME_HEADER: str = "X-Process-Time"

    # Paths that never emit request start/complete lines (still get a
    # request-id/process-time response header). Not env-driven — extend in
    # code where the app is built, e.g. LoggingConfig(skip_paths=...).
    skip_paths: tuple[str, ...] = (
        "/health",
        "/healthz",
        "/ready",
        "/docs",
        "/redoc",
        "/openapi.json",
    )

    # Incoming header (case-insensitive) -> extra field name to attach to
    # request logs. "authorization" and "cookie" are always ignored.
    extra_headers: dict[str, str] = {}


@lru_cache
def get_logging_config() -> LoggingConfig:
    return LoggingConfig()
