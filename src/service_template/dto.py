import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, field_validator

# TODO: replace ExampleModel* with your domain entity name, e.g. ProductCreate.


class ExampleModelCreate(BaseModel):
    name: str = Field(max_length=255)
    meta: dict[str, Any] | None = None


class ExampleModelUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=255)
    meta: dict[str, Any] | None = None

    @field_validator("name")
    @classmethod
    def non_null_name(cls, value):
        if value is None:
            raise ValueError("Name cannot be null")
        return value


class ExampleModelRead(BaseModel):
    id: int
    uid: uuid.UUID
    name: str
    meta: dict[str, Any] | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
