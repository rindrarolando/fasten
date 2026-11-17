from fastapi import APIRouter

from src.auth.dependencies import CurrentUser
from src.auth.dto import Principal

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/me", response_model=Principal)
async def me(user: CurrentUser) -> Principal:
    return user
