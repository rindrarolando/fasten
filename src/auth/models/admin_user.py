import uuid
from datetime import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from src.async_database import Base
from src.auth.enums.enum import AdminUserRole
from src.db_types import FormattedUUID


class AdminUser(Base):
    __tablename__ = "admin_user"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    uid: Mapped[uuid.UUID] = mapped_column(
        FormattedUUID(), unique=True, nullable=False, default=uuid.uuid4
    )
    username: Mapped[str] = mapped_column(String(150), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(
        String(20), nullable=False, default=AdminUserRole.ADMIN.value
    )
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )
