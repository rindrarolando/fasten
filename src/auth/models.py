import uuid
from datetime import datetime

from sqlalchemy import Boolean, CheckConstraint, DateTime, String, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column

from src.async_database import Base


class User(Base):
    __tablename__ = "app_user"
    __table_args__ = (
        CheckConstraint("role IN ('USER', 'ADMIN', 'SUPERADMIN')", name="role"),
    )
    uid: Mapped[uuid.UUID] = mapped_column(Uuid(), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(320), nullable=False, unique=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False, default="USER")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
