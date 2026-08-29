from __future__ import annotations

import functools
import inspect
import logging
import time
from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any, Callable, TypeVar

F = TypeVar("F", bound=Callable[..., Any])


@contextmanager
def operation_logger(
    name: str,
    *,
    feature: str,
    logger: logging.Logger | None = None,
    **extra_fields: Any,
) -> Iterator[None]:
    """
    Context-manager form of `@operation_log`, for blocks that are not a
    method (script steps, inner loops, worker jobs).
    """
    log = logger or logging.getLogger(__name__)
    base_extra = {"operation": name, "feature": feature, **extra_fields}
    start = time.perf_counter()

    log.info("Starting operation: %s", name, extra=base_extra)
    try:
        yield
    except Exception as exc:
        duration_ms = round((time.perf_counter() - start) * 1000, 2)
        log.error(
            "Failed operation: %s",
            name,
            extra={
                **base_extra,
                "duration_ms": duration_ms,
                "error": str(exc),
                "error_type": type(exc).__name__,
            },
            exc_info=True,
        )
        raise
    else:
        duration_ms = round((time.perf_counter() - start) * 1000, 2)
        log.info(
            "Completed operation: %s",
            name,
            extra={**base_extra, "duration_ms": duration_ms},
        )


def operation_log(name: str, *, feature: str, **extra_fields: Any) -> Callable[[F], F]:
    """
    @operation_log("create_order", feature="orders")
    async def create_order(self, ...): ...

    Logs start / complete (+ duration_ms) / failed (+ error, exc_info) on the
    module logger of the wrapped function. Works on sync and async callables.
    """

    def decorator(func: F) -> F:
        logger = logging.getLogger(func.__module__)

        if inspect.iscoroutinefunction(func):

            @functools.wraps(func)
            async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
                with operation_logger(name, feature=feature, logger=logger, **extra_fields):
                    return await func(*args, **kwargs)

            return async_wrapper  # type: ignore[return-value]

        @functools.wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            with operation_logger(name, feature=feature, logger=logger, **extra_fields):
                return func(*args, **kwargs)

        return sync_wrapper  # type: ignore[return-value]

    return decorator
