from threading import Lock

import httpx
import jwt
from fastapi import HTTPException
from starlette.concurrency import run_in_threadpool

from src.auth.config import AuthConfig
from src.auth.dto import Principal


class AuthService:
    """Verify provider-issued access JWTs. Never accept local passwords or ID tokens."""

    def __init__(self, config: AuthConfig) -> None:
        self._config = config
        self._jwks: jwt.PyJWKClient | None = None
        self._lock = Lock()

    def _get_jwks(self) -> jwt.PyJWKClient:
        with self._lock:
            if self._jwks is None:
                url = (
                    self._config.OIDC_ISSUER.rstrip("/")
                    + "/.well-known/openid-configuration"
                )
                response = httpx.get(url, timeout=5, follow_redirects=False)
                response.raise_for_status()
                metadata = response.json()
                if metadata.get("issuer") != self._config.OIDC_ISSUER:
                    raise ValueError("Discovery issuer mismatch")
                jwks_uri = self._config.validate_url(metadata["jwks_uri"])
                self._jwks = jwt.PyJWKClient(
                    jwks_uri, lifespan=self._config.OIDC_JWKS_CACHE_SECONDS, timeout=5
                )
            return self._jwks

    async def authenticate(self, token: str) -> Principal:
        # Discovery/JWKS clients are synchronous; keep network IO off the event loop.
        return await run_in_threadpool(self._authenticate, token)

    def _authenticate(self, token: str) -> Principal:
        try:
            header = jwt.get_unverified_header(token)
            if (
                header.get("alg") != "RS256"
                or not isinstance(header.get("kid"), str)
                or not header["kid"]
            ):
                raise jwt.InvalidTokenError("Unsupported signing header")
            key = self._get_jwks().get_signing_key_from_jwt(token).key
            claims = jwt.decode(
                token,
                key,
                algorithms=["RS256"],
                audience=self._config.OIDC_AUDIENCE,
                issuer=self._config.OIDC_ISSUER,
                options={"require": ["exp", "iat", "iss", "aud", "sub"]},
            )
            if not isinstance(claims["sub"], str) or not claims["sub"]:
                raise jwt.InvalidTokenError("Missing subject")
            path = self._config.OIDC_ROLES_CLAIM
            roles = claims.get(path)
            if roles is None:
                roles = claims
                for part in path.split("."):
                    roles = roles.get(part, []) if isinstance(roles, dict) else []
            if not isinstance(roles, list) or any(
                not isinstance(role, str) for role in roles
            ):
                raise jwt.InvalidTokenError("Invalid role claim")
            return Principal(subject=claims["sub"], issuer=claims["iss"], roles=roles)
        except jwt.PyJWKClientConnectionError:
            raise HTTPException(503, "Identity provider unavailable") from None
        except jwt.PyJWTError:
            raise HTTPException(
                401, "Invalid access token", headers={"WWW-Authenticate": "Bearer"}
            ) from None
        except (httpx.HTTPError, ValueError, KeyError, TypeError):
            raise HTTPException(
                503, "Identity provider unavailable or misconfigured"
            ) from None
