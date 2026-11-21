import uuid
from typing import Any

from sqlalchemy import delete, func, select, update

from src.async_database import AsyncDatabase
from src.service_template.models.example import ExampleModel


# TODO: rename to <ServiceName>Dal and add methods for each model you define.
class ServiceDal:
    def __init__(self, db: AsyncDatabase) -> None:
        self._db = db

    # ------------------------------------------------------------------
    # ExampleModel CRUD
    # ------------------------------------------------------------------

    async def create(self, data: dict[str, Any]) -> ExampleModel:
        async with self._db.session() as session:
            obj = ExampleModel(**data)
            session.add(obj)
            await session.commit()
            await session.refresh(obj)
            return obj

    async def get_by_uid(self, uid: uuid.UUID) -> ExampleModel | None:
        async with self._db.session() as session:
            result = await session.execute(
                select(ExampleModel).where(ExampleModel.uid == uid)
            )
            return result.scalar_one_or_none()

    async def list(self, page: int, size: int) -> tuple[list[ExampleModel], int]:
        async with self._db.session() as session:
            total_result = await session.execute(
                select(func.count()).select_from(ExampleModel)
            )
            total = total_result.scalar_one()
            result = await session.execute(
                select(ExampleModel)
                .order_by(ExampleModel.created_at.desc())
                .offset((page - 1) * size)
                .limit(size)
            )
            return list(result.scalars().all()), total

    async def update(self, uid: uuid.UUID, data: dict[str, Any]) -> ExampleModel | None:
        async with self._db.session() as session:
            # An empty PATCH is a read-only no-op; do not change updated_at.
            if not data:
                return await session.scalar(
                    select(ExampleModel).where(ExampleModel.uid == uid)
                )
            obj = await session.scalar(
                update(ExampleModel)
                .where(ExampleModel.uid == uid)
                .values(**data)
                .returning(ExampleModel)
            )
            await session.commit()
            return obj

    async def delete(self, uid: uuid.UUID) -> bool:
        async with self._db.session() as session:
            deleted = await session.scalar(
                delete(ExampleModel)
                .where(ExampleModel.uid == uid)
                .returning(ExampleModel.uid)
            )
            await session.commit()
            return deleted is not None
