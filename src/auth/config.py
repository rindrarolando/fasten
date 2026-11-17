from urllib.parse import urlparse

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class AuthConfig(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    OIDC_ISSUER: str
    OIDC_AUDIENCE: str = Field(min_length=1)
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
        self.validate_url(self.OIDC_ISSUER)
        if not self.OIDC_ROLES_CLAIM or any(
            not part for part in self.OIDC_ROLES_CLAIM.split(".")
        ):
            raise ValueError("OIDC_ROLES_CLAIM must be a dot-separated claim path")
        return self
