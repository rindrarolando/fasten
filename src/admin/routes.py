from fastapi import APIRouter

from src.admin.dto import MessageResponse

router = APIRouter(prefix="/admin", tags=["admin"])

# Admin routes are protected by verify_admin_credentials (v2).
# Stubs are provided here as placeholders for future implementation.


@router.get(
    "/health",
    response_model=MessageResponse,
    summary="Admin health check",
)
async def admin_health() -> MessageResponse:
    return MessageResponse(message="Admin service is up.")
