from __future__ import annotations

import logging
import time
import uuid
from typing import Any

from starlette.types import ASGIApp, Receive, Scope, Send

from src.log.config import LoggingConfig
from src.log.context import (
    bind_log_context,
    reset_log_context,
    reset_request_id,
    set_request_id,
)

logger = logging.getLogger("src.log.request")

_IGNORED_EXTRA_HEADERS = {"authorization", "cookie"}


class RequestLoggingMiddleware:
    """
    Pure ASGI middleware. Register it last (outermost) so every request gets
    a request id before anything else runs:

        app.add_middleware(RequestLoggingMiddleware, settings=get_logging_config())
    """

    def __init__(self, app: ASGIApp, settings: LoggingConfig) -> None:
        self._app = app
        self._settings = settings

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self._app(scope, receive, send)
            return

        headers = {
            key.decode("latin-1").lower(): value.decode("latin-1")
            for key, value in scope["headers"]
        }
        path = scope["path"]

        incoming_request_id = headers.get(self._settings.LOG_REQUEST_ID_HEADER.lower())
        request_id = incoming_request_id or str(uuid.uuid4())
        request_id_source = "client" if incoming_request_id else "generated"

        request_id_token = set_request_id(request_id)
        context_token = bind_log_context()

        skip = path in self._settings.skip_paths

        extra_fields: dict[str, Any] = {}
        for header_name, field_name in self._settings.extra_headers.items():
            lname = header_name.lower()
            if lname in _IGNORED_EXTRA_HEADERS:
                continue
            if lname in headers:
                extra_fields[field_name] = headers[lname]

        client = scope.get("client")
        forwarded_for = headers.get("x-forwarded-for", "")
        client_ip = forwarded_for.split(",")[0].strip() or (client[0] if client else None)

        base_fields = {
            "request_method": scope["method"],
            "request_path": path,
            "client_ip": client_ip,
            "user_agent": headers.get("user-agent"),
            "request_id": request_id,
            "request_id_source": request_id_source,
            **extra_fields,
        }

        start = time.perf_counter()
        status_code = 500

        async def send_wrapper(message: dict[str, Any]) -> None:
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = message["status"]
                duration_ms = round((time.perf_counter() - start) * 1000, 2)
                response_headers = message.setdefault("headers", [])
                response_headers.append(
                    (
                        self._settings.LOG_REQUEST_ID_HEADER.encode("latin-1"),
                        request_id.encode("latin-1"),
                    )
                )
                response_headers.append(
                    (
                        self._settings.LOG_PROCESS_TIME_HEADER.encode("latin-1"),
                        f"{duration_ms}ms".encode("latin-1"),
                    )
                )
            await send(message)

        if not skip:
            logger.info("Request started", extra=base_fields)

        try:
            await self._app(scope, receive, send_wrapper)
        except Exception as exc:
            duration_ms = round((time.perf_counter() - start) * 1000, 2)
            logger.error(
                "Request failed",
                extra={
                    **base_fields,
                    "duration_ms": duration_ms,
                    "error": str(exc),
                    "error_type": type(exc).__name__,
                },
                exc_info=True,
            )
            raise
        else:
            if not skip:
                duration_ms = round((time.perf_counter() - start) * 1000, 2)
                logger.info(
                    "Request completed",
                    extra={**base_fields, "status_code": status_code, "duration_ms": duration_ms},
                )
        finally:
            reset_request_id(request_id_token)
            reset_log_context(context_token)
