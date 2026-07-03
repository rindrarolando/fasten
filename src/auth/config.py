from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class AuthConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    CLIENT_SHARED_SECRET: str = "change_me_in_production"
    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str = "admin_pwd1234"


@lru_cache
def get_auth_config() -> AuthConfig:
    return AuthConfig()
