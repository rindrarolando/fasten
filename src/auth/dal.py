import uuid
from typing import Any

from sqlalchemy import delete, func, select, update

from src.async_database import AsyncDatabase
from src.auth.models.admin_user import AdminUser


class AuthDal:
    def __init__(self, db: AsyncDatabase) -> None:
        self._db = db

    # ------------------------------------------------------------------
    # AdminUser CRUD
    # ------------------------------------------------------------------

    async def create(self, data: dict[str, Any]) -> AdminUser:
        async with self._db.session() as session:
            obj = AdminUser(**data)
            session.add(obj)
            await session.commit()
            await session.refresh(obj)
            return obj

    async def get_by_username(self, username: str) -> AdminUser | None:
        async with self._db.session() as session:
            result = await session.execute(
                select(AdminUser).where(AdminUser.username == username)
            )
            return result.scalar_one_or_none()

    async def get_by_uid(self, uid: uuid.UUID) -> AdminUser | None:
        async with self._db.session() as session:
            result = await session.execute(
                select(AdminUser).where(AdminUser.uid == uid)
            )
            return result.scalar_one_or_none()

    async def list(self, page: int, size: int) -> tuple[list[AdminUser], int]:
        async with self._db.session() as session:
            total_result = await session.execute(
                select(func.count()).select_from(AdminUser)
            )
            total = total_result.scalar_one()
            result = await session.execute(
                select(AdminUser)
                .order_by(AdminUser.created_at.desc())
                .offset((page - 1) * size)
                .limit(size)
            )
            return list(result.scalars().all()), total

    async def update(self, obj_id: int, data: dict[str, Any]) -> AdminUser | None:
        async with self._db.session() as session:
            await session.execute(
                update(AdminUser).where(AdminUser.id == obj_id).values(**data)
            )
            await session.commit()
            return await session.get(AdminUser, obj_id)

    async def delete(self, obj_id: int) -> None:
        async with self._db.session() as session:
            await session.execute(
                delete(AdminUser).where(AdminUser.id == obj_id)
            )
            await session.commit()
