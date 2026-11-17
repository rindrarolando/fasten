from typing import Annotated

from dependency_injector.wiring import Provide, inject
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.auth.dto import Principal
from src.auth.service import AuthService

bearer = HTTPBearer(
    auto_error=False, description="OIDC access token for this API's audience"
)


@inject
async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)],
    auth_service: AuthService = Depends(Provide["auth.service"]),
) -> Principal:
    if credentials is None:
        raise HTTPException(
            401, "Bearer token required", headers={"WWW-Authenticate": "Bearer"}
        )
    return await auth_service.authenticate(credentials.credentials)


CurrentUser = Annotated[Principal, Depends(get_current_user)]


def require_roles(*roles: str):
    """Require at least one exact, provider-assigned role; no implicit hierarchy."""

    async def check(user: CurrentUser) -> Principal:
        if not set(roles).intersection(user.roles):
            raise HTTPException(403, "Insufficient permissions")
        return user

    return check
