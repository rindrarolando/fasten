from fastapi import APIRouter
from fastapi.responses import JSONResponse

from src.auth.dto import AdminLoginRequest, AdminLoginResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/admin/login",
    response_model=AdminLoginResponse,
    status_code=501,
    summary="Admin login (not implemented — v2)",
)
async def admin_login(body: AdminLoginRequest) -> JSONResponse:
    return JSONResponse(
        status_code=501,
        content={"message": "Admin login is not implemented yet. Planned for v2."},
    )
