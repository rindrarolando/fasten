import uuid
from typing import Any

from sqlalchemy import select, update, delete, func

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

    async def update(self, obj_id: int, data: dict[str, Any]) -> ExampleModel | None:
        async with self._db.session() as session:
            await session.execute(
                update(ExampleModel).where(ExampleModel.id == obj_id).values(**data)
            )
            await session.commit()
            return await session.get(ExampleModel, obj_id)

    async def delete(self, obj_id: int) -> None:
        async with self._db.session() as session:
            await session.execute(
                delete(ExampleModel).where(ExampleModel.id == obj_id)
            )
            await session.commit()
