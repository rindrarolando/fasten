import uuid

from fastapi import APIRouter, Depends, Query
from dependency_injector.wiring import Provide, inject

from src.auth.dependencies import verify_client_secret
from src.utils import PaginatedResponse
from src.service_template.dto import (
    ExampleModelCreate,
    ExampleModelUpdate,
    ExampleModelRead,
)
from src.service_template.service import ServiceLayer

# TODO: update the prefix to match your service, e.g. /api/v1.
router = APIRouter(
    prefix="/api/v1",
    tags=["service_template"],
    dependencies=[Depends(verify_client_secret)],
)


@router.get("/examples", response_model=PaginatedResponse[ExampleModelRead])
@inject
async def list_examples(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=10, ge=1, le=100),
    # TODO: update the Provide key to match your container, e.g. "my_service.service".
    service: ServiceLayer = Depends(Provide["service_template.service"]),
) -> PaginatedResponse[ExampleModelRead]:
    return await service.list(page=page, size=size)


@router.post("/examples", response_model=ExampleModelRead, status_code=201)
@inject
async def create_example(
    body: ExampleModelCreate,
    service: ServiceLayer = Depends(Provide["service_template.service"]),
) -> ExampleModelRead:
    return await service.create(body)


@router.get("/examples/{uid}", response_model=ExampleModelRead)
@inject
async def get_example(
    uid: uuid.UUID,
    service: ServiceLayer = Depends(Provide["service_template.service"]),
) -> ExampleModelRead:
    return await service.get(uid)


@router.patch("/examples/{uid}", response_model=ExampleModelRead)
@inject
async def update_example(
    uid: uuid.UUID,
    body: ExampleModelUpdate,
    service: ServiceLayer = Depends(Provide["service_template.service"]),
) -> ExampleModelRead:
    return await service.update(uid, body)


@router.delete("/examples/{uid}", status_code=204)
@inject
async def delete_example(
    uid: uuid.UUID,
    service: ServiceLayer = Depends(Provide["service_template.service"]),
) -> None:
    await service.delete(uid)
