import uuid

from fastapi import APIRouter, Depends, Query
from dependency_injector.wiring import Provide, inject

from src.auth.dependencies import verify_admin_credentials
from src.auth.dto import (
    AdminLoginRequest,
    AdminLoginResponse,
    AdminUserCreate,
    AdminUserRead,
    AdminUserUpdate,
)
from src.auth.errors import InvalidAdminCredentials
from src.auth.service import AuthService
from src.utils import PaginatedResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/admin/login",
    response_model=AdminLoginResponse,
    summary="Admin login",
)
@inject
async def admin_login(
    body: AdminLoginRequest,
    auth_service: AuthService = Depends(Provide["auth.service"]),
) -> AdminLoginResponse:
    if not await auth_service.verify_admin_credentials(body.username, body.password):
        raise InvalidAdminCredentials()
    return AdminLoginResponse(message="Login successful.")


# Admin-user management. Protected by verify_admin_credentials
# (X-Admin-Username / X-Admin-Password headers).
admin_users_router = APIRouter(
    prefix="/auth/admin/users",
    tags=["auth"],
    dependencies=[Depends(verify_admin_credentials)],
)


@admin_users_router.get("", response_model=PaginatedResponse[AdminUserRead])
@inject
async def list_admin_users(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=10, ge=1, le=100),
    auth_service: AuthService = Depends(Provide["auth.service"]),
) -> PaginatedResponse[AdminUserRead]:
    return await auth_service.list_admin_users(page=page, size=size)


@admin_users_router.post("", response_model=AdminUserRead, status_code=201)
@inject
async def create_admin_user(
    body: AdminUserCreate,
    auth_service: AuthService = Depends(Provide["auth.service"]),
) -> AdminUserRead:
    return await auth_service.create_admin_user(body)


@admin_users_router.get("/{uid}", response_model=AdminUserRead)
@inject
async def get_admin_user(
    uid: uuid.UUID,
    auth_service: AuthService = Depends(Provide["auth.service"]),
) -> AdminUserRead:
    return await auth_service.get_admin_user(uid)


@admin_users_router.patch("/{uid}", response_model=AdminUserRead)
@inject
async def update_admin_user(
    uid: uuid.UUID,
    body: AdminUserUpdate,
    auth_service: AuthService = Depends(Provide["auth.service"]),
) -> AdminUserRead:
    return await auth_service.update_admin_user(uid, body)


@admin_users_router.delete("/{uid}", status_code=204)
@inject
async def delete_admin_user(
    uid: uuid.UUID,
    auth_service: AuthService = Depends(Provide["auth.service"]),
) -> None:
    await auth_service.delete_admin_user(uid)
