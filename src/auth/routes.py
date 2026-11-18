from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException

from src.auth.dependencies import CurrentUser
from src.auth.dto import Credentials, Principal, RegisterRequest, TokenResponse
from src.auth.local import LocalAuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/me", response_model=Principal)
async def me(user: CurrentUser) -> Principal:
    return user


@router.post("/login", response_model=TokenResponse)
@inject
async def login(body: Credentials, service=Depends(Provide["auth.service"])):
    if not isinstance(service, LocalAuthService):
        raise HTTPException(404, "Local authentication disabled")
    return await service.login(body)


@router.post("/register", response_model=Principal, status_code=201)
@inject
async def register(body: RegisterRequest, service=Depends(Provide["auth.service"])):
    if (
        not isinstance(service, LocalAuthService)
        or not service.config.AUTH_ALLOW_REGISTRATION
    ):
        raise HTTPException(404, "Registration disabled")
    return await service.create_user(body)
