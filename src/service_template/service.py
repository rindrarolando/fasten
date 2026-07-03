import uuid

from src.utils import PaginatedResponse, paginate
from src.service_template.dal import ServiceDal
from src.service_template.dto import (
    ExampleModelCreate,
    ExampleModelUpdate,
    ExampleModelRead,
)
from src.service_template.errors import ExampleModelNotFound
from src.service_template.services.example_worker import ExampleWorker


# TODO: rename to <ServiceName>Service and update method names / logic.
class ServiceLayer:
    def __init__(self, dal: ServiceDal, example_worker: ExampleWorker) -> None:
        self._dal = dal
        self._example_worker = example_worker

    async def create(self, body: ExampleModelCreate) -> ExampleModelRead:
        obj = await self._dal.create(
            {
                "uid": uuid.uuid4(),
                "name": body.name,
                "meta": body.meta,
            }
        )
        return ExampleModelRead.model_validate(obj)

    @paginate(default_limit=50)
    async def list(self, page: int, size: int) -> tuple[list[ExampleModelRead], int]:
        items, total = await self._dal.list(page, size)
        return [ExampleModelRead.model_validate(i) for i in items], total

    async def get(self, uid: uuid.UUID) -> ExampleModelRead:
        obj = await self._dal.get_by_uid(uid)
        if obj is None:
            raise ExampleModelNotFound(str(uid))
        return ExampleModelRead.model_validate(obj)

    async def update(self, uid: uuid.UUID, body: ExampleModelUpdate) -> ExampleModelRead:
        obj = await self._dal.get_by_uid(uid)
        if obj is None:
            raise ExampleModelNotFound(str(uid))
        updates = body.model_dump(exclude_none=True)
        updated = await self._dal.update(obj.id, updates)
        return ExampleModelRead.model_validate(updated)

    async def delete(self, uid: uuid.UUID) -> None:
        obj = await self._dal.get_by_uid(uid)
        if obj is None:
            raise ExampleModelNotFound(str(uid))
        await self._dal.delete(obj.id)
