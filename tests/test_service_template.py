import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock

import pytest
from pydantic import ValidationError

from src.service_template.dto import ExampleModelCreate, ExampleModelUpdate
from src.service_template.errors import ExampleModelNotFound
from src.service_template.models.example import ExampleModel
from src.service_template.service import ServiceLayer


@pytest.mark.parametrize("model", [ExampleModelCreate, ExampleModelUpdate])
def test_name_matches_database_limit(model):
    assert model(name="x" * 255).name == "x" * 255
    with pytest.raises(ValidationError):
        model(name="x" * 256)
    with pytest.raises(ValidationError):
        model(name=None)


@pytest.mark.parametrize(
    "payload", [{}, {"meta": None}, {"name": "renamed"}]
)
async def test_patch_preserves_explicit_fields(payload):
    uid = uuid.uuid4()
    now = datetime.now(timezone.utc)
    dal = AsyncMock()
    dal.update.return_value = ExampleModel(
        id=1, uid=uid, name="example", meta=None,
        created_at=now, updated_at=now,
    )
    service = ServiceLayer(dal=dal, example_worker=AsyncMock())
    result = await service.update(uid, ExampleModelUpdate(**payload))
    assert result.uid == uid
    dal.update.assert_awaited_once_with(uid, payload)
    dal.get_by_uid.assert_not_awaited()


async def test_patch_deleted_record_returns_not_found():
    uid = uuid.uuid4()
    dal = AsyncMock()
    dal.update.return_value = None
    service = ServiceLayer(dal=dal, example_worker=AsyncMock())
    with pytest.raises(ExampleModelNotFound) as error:
        await service.update(uid, ExampleModelUpdate(name="renamed"))
    assert error.value.status_code == 404
    dal.get_by_uid.assert_not_awaited()


@pytest.mark.parametrize("deleted", [True, False])
async def test_delete_uses_atomic_result(deleted):
    uid = uuid.uuid4()
    dal = AsyncMock()
    dal.delete.return_value = deleted
    service = ServiceLayer(dal=dal, example_worker=AsyncMock())
    if deleted:
        await service.delete(uid)
    else:
        with pytest.raises(ExampleModelNotFound):
            await service.delete(uid)
    dal.delete.assert_awaited_once_with(uid)
    dal.get_by_uid.assert_not_awaited()
