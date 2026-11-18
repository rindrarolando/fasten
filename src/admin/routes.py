from fastapi import APIRouter, Depends

from src.admin.dto import MessageResponse
from src.auth.dependencies import require_roles

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(require_roles("ADMIN", "SUPERADMIN"))],
)


@router.get(
    "/health",
    response_model=MessageResponse,
    summary="Admin health check",
)
async def admin_health() -> MessageResponse:
    return MessageResponse(message="Admin service is up.")
