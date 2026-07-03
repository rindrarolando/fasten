import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import BigInteger, String, DateTime, JSON, func
from sqlalchemy.orm import Mapped, mapped_column

from src.async_database import Base
from src.db_types import FormattedUUID


# TODO: rename this class to your domain entity (e.g. Product, Order).
#       Add / remove columns to match your schema.
class ExampleModel(Base):
    __tablename__ = "example"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    uid: Mapped[uuid.UUID] = mapped_column(
        FormattedUUID(), unique=True, nullable=False, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    meta: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )
