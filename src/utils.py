import functools
from datetime import datetime, timezone
from typing import Any, Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    size: int


def paginate(default_limit: int = 50):
    """
    Service-layer decorator. The decorated coroutine must accept `page` and
    `size` keyword arguments and return `(items, total)`. The decorator wraps
    that tuple into a `PaginatedResponse` and uses `default_limit` when the
    caller passes `size=None`.
    """
    def decorator(func: Any) -> Any:
        @functools.wraps(func)
        async def wrapper(*args: Any, page: int = 1, size: int | None = None, **kwargs: Any) -> PaginatedResponse:  # type: ignore[type-arg]
            effective = size if size is not None else default_limit
            items, total = await func(*args, page=page, size=effective, **kwargs)
            return PaginatedResponse(items=items, total=total, page=page, size=effective)
        return wrapper
    return decorator
