import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel


# TODO: replace ExampleModel* with your domain entity name, e.g. ProductCreate.


class ExampleModelCreate(BaseModel):
    name: str
    meta: dict[str, Any] | None = None


class ExampleModelUpdate(BaseModel):
    name: str | None = None
    meta: dict[str, Any] | None = None


class ExampleModelRead(BaseModel):
    id: int
    uid: uuid.UUID
    name: str
    meta: dict[str, Any] | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
