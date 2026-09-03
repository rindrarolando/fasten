import uuid
from datetime import datetime

from pydantic import BaseModel

from src.auth.enums.enum import AdminUserRole


class AdminLoginRequest(BaseModel):
    username: str
    password: str


class AdminLoginResponse(BaseModel):
    message: str


class AdminUserCreate(BaseModel):
    username: str
    password: str
    role: AdminUserRole = AdminUserRole.ADMIN


class AdminUserUpdate(BaseModel):
    password: str | None = None
    role: AdminUserRole | None = None
    is_active: bool | None = None


class AdminUserRead(BaseModel):
    id: int
    uid: uuid.UUID
    username: str
    role: AdminUserRole
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
