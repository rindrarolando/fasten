from fastapi import Depends, Header
from dependency_injector.wiring import Provide, inject

from src.auth.errors import InvalidClientSecret, InvalidAdminCredentials
from src.auth.service import AuthService


@inject
async def verify_client_secret(
    x_client_secret: str = Header(alias="X-Client-Secret", default=""),
    auth_service: AuthService = Depends(Provide["auth.service"]),
) -> None:
    if not auth_service.verify_client_secret(x_client_secret):
        raise InvalidClientSecret()


@inject
async def verify_admin_credentials(
    x_admin_username: str = Header(alias="X-Admin-Username", default=""),
    x_admin_password: str = Header(alias="X-Admin-Password", default=""),
    auth_service: AuthService = Depends(Provide["auth.service"]),
) -> None:
    """
    Validates admin credentials from request headers against the DB-backed
    admin_user table. Will be replaced by proper JWT in a future version.
    """
    if not await auth_service.verify_admin_credentials(x_admin_username, x_admin_password):
        raise InvalidAdminCredentials()
