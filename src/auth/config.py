from typing import Literal
from urllib.parse import urlparse

from pydantic import Field, SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class AuthConfig(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    AUTH_MODE: Literal["local", "oidc"] = "local"
    JWT_SECRET_KEY: SecretStr | None = None
    JWT_ISSUER: str = "fasten"
    JWT_AUDIENCE: str = "fasten-api"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, ge=1, le=1440)
    AUTH_ALLOW_REGISTRATION: bool = False

    OIDC_ISSUER: str | None = None
    OIDC_AUDIENCE: str | None = None
    OIDC_ROLES_CLAIM: str = "roles"
    OIDC_ALLOW_INSECURE_HTTP: bool = False
    OIDC_JWKS_CACHE_SECONDS: int = Field(default=300, ge=30, le=3600)

    def validate_url(self, value: str) -> str:
        parsed = urlparse(value)
        if (
            not parsed.hostname
            or parsed.username
            or parsed.password
            or parsed.query
            or parsed.fragment
        ):
            raise ValueError(
                "OIDC URLs must be absolute URLs without credentials, query or fragment"
            )
        if parsed.scheme != "https" and not (
            self.OIDC_ALLOW_INSECURE_HTTP and parsed.scheme == "http"
        ):
            raise ValueError(
                "OIDC requires HTTPS; insecure HTTP is for local development only"
            )
        return value

    @model_validator(mode="after")
    def validate_provider(self):
        if self.AUTH_MODE == "local":
            if (
                not self.JWT_SECRET_KEY
                or len(self.JWT_SECRET_KEY.get_secret_value()) < 32
            ):
                raise ValueError(
                    "Local auth requires JWT_SECRET_KEY with at least 32 characters"
                )
            return self
        if not self.OIDC_ISSUER or not self.OIDC_AUDIENCE:
            raise ValueError("OIDC mode requires OIDC_ISSUER and OIDC_AUDIENCE")
        self.validate_url(self.OIDC_ISSUER)
        if not self.OIDC_ROLES_CLAIM or any(
            not part for part in self.OIDC_ROLES_CLAIM.split(".")
        ):
            raise ValueError("OIDC_ROLES_CLAIM must be a dot-separated claim path")
        return self
