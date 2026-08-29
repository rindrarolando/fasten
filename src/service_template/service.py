import uuid

from src.utils import PaginatedResponse, paginate
from src.log import get_feature_logger, operation_log
from src.service_template.dal import ServiceDal
from src.service_template.dto import (
    ExampleModelCreate,
    ExampleModelUpdate,
    ExampleModelRead,
)
from src.service_template.errors import ExampleModelNotFound
from src.service_template.services.example_worker import ExampleWorker

# TODO: rename "service_template" to your bounded-context name, e.g. "orders".
logger = get_feature_logger(__name__, feature="service_template")


# TODO: rename to <ServiceName>Service and update method names / logic.
class ServiceLayer:
    def __init__(self, dal: ServiceDal, example_worker: ExampleWorker) -> None:
        self._dal = dal
        self._example_worker = example_worker

    @operation_log("create_example", feature="service_template")
    async def create(self, body: ExampleModelCreate) -> ExampleModelRead:
        obj = await self._dal.create(
            {
                "uid": uuid.uuid4(),
                "name": body.name,
                "meta": body.meta,
            }
        )
        logger.info("Example created", extra={"uid": str(obj.uid)})
        return ExampleModelRead.model_validate(obj)

    @paginate(default_limit=50)
    @operation_log("list_examples", feature="service_template")
    async def list(self, page: int, size: int) -> tuple[list[ExampleModelRead], int]:
        items, total = await self._dal.list(page, size)
        return [ExampleModelRead.model_validate(i) for i in items], total

    @operation_log("get_example", feature="service_template")
    async def get(self, uid: uuid.UUID) -> ExampleModelRead:
        obj = await self._dal.get_by_uid(uid)
        if obj is None:
            raise ExampleModelNotFound(str(uid))
        return ExampleModelRead.model_validate(obj)

    @operation_log("update_example", feature="service_template")
    async def update(self, uid: uuid.UUID, body: ExampleModelUpdate) -> ExampleModelRead:
        obj = await self._dal.get_by_uid(uid)
        if obj is None:
            raise ExampleModelNotFound(str(uid))
        updates = body.model_dump(exclude_none=True)
        updated = await self._dal.update(obj.id, updates)
        return ExampleModelRead.model_validate(updated)

    @operation_log("delete_example", feature="service_template")
    async def delete(self, uid: uuid.UUID) -> None:
        obj = await self._dal.get_by_uid(uid)
        if obj is None:
            raise ExampleModelNotFound(str(uid))
        await self._dal.delete(obj.id)
