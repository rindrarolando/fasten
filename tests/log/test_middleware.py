import logging

import pytest

from src.log.config import LoggingConfig
from src.log.context import get_request_id
from src.log.middleware import RequestLoggingMiddleware


def _scope(path: str = "/orders", headers: list[tuple[bytes, bytes]] | None = None) -> dict:
    return {
        "type": "http",
        "method": "GET",
        "path": path,
        "headers": headers or [],
        "client": ("127.0.0.1", 1234),
    }


async def _receive() -> dict:
    return {"type": "http.request", "body": b"", "more_body": False}


class _Collector:
    def __init__(self) -> None:
        self.messages: list[dict] = []

    async def __call__(self, message: dict) -> None:
        self.messages.append(message)

    def header(self, name: bytes) -> bytes | None:
        start = next(m for m in self.messages if m["type"] == "http.response.start")
        for key, value in start["headers"]:
            if key.lower() == name.lower():
                return value
        return None


async def _ok_app(scope, receive, send) -> None:
    await send({"type": "http.response.start", "status": 200, "headers": []})
    await send({"type": "http.response.body", "body": b"{}"})


async def _failing_app(scope, receive, send) -> None:
    raise RuntimeError("db down")


class TestRequestLoggingMiddlewareHappyPath:
    async def test_logs_start_and_complete_and_sets_headers(self, caplog):
        middleware = RequestLoggingMiddleware(_ok_app, settings=LoggingConfig())
        collector = _Collector()

        with caplog.at_level(logging.INFO, logger="src.log.request"):
            await middleware(_scope(), _receive, collector)

        messages = [r.getMessage() for r in caplog.records]
        assert "Request started" in messages
        completed = next(r for r in caplog.records if r.getMessage() == "Request completed")
        assert completed.status_code == 200
        assert completed.duration_ms >= 0
        assert completed.request_path == "/orders"

        assert collector.header(b"X-Request-ID") is not None
        assert collector.header(b"X-Process-Time").endswith(b"ms")

    async def test_clears_request_id_context_after_request(self):
        middleware = RequestLoggingMiddleware(_ok_app, settings=LoggingConfig())
        await middleware(_scope(), _receive, _Collector())
        assert get_request_id() is None

    async def test_echoes_incoming_request_id(self, caplog):
        middleware = RequestLoggingMiddleware(_ok_app, settings=LoggingConfig())
        collector = _Collector()
        headers = [(b"x-request-id", b"client-req-1")]

        with caplog.at_level(logging.INFO, logger="src.log.request"):
            await middleware(_scope(headers=headers), _receive, collector)

        started = next(r for r in caplog.records if r.getMessage() == "Request started")
        assert started.request_id == "client-req-1"
        assert started.request_id_source == "client"
        assert collector.header(b"X-Request-ID") == b"client-req-1"


class TestRequestLoggingMiddlewareException:
    async def test_logs_failure_and_reraises(self, caplog):
        middleware = RequestLoggingMiddleware(_failing_app, settings=LoggingConfig())

        with caplog.at_level(logging.INFO, logger="src.log.request"):
            with pytest.raises(RuntimeError, match="db down"):
                await middleware(_scope(), _receive, _Collector())

        failed = next(r for r in caplog.records if r.getMessage() == "Request failed")
        assert failed.error == "db down"
        assert failed.error_type == "RuntimeError"


class TestRequestLoggingMiddlewareSkipPaths:
    async def test_no_start_complete_logs_for_skip_path(self, caplog):
        middleware = RequestLoggingMiddleware(_ok_app, settings=LoggingConfig())

        with caplog.at_level(logging.INFO, logger="src.log.request"):
            await middleware(_scope(path="/health"), _receive, _Collector())

        assert caplog.records == []


class TestRequestLoggingMiddlewareExtraHeaders:
    async def test_configured_header_is_attached(self, caplog):
        settings = LoggingConfig(extra_headers={"x-tenant-id": "tenant_id"})
        middleware = RequestLoggingMiddleware(_ok_app, settings=settings)
        headers = [(b"x-tenant-id", b"tenant-42"), (b"x-other", b"ignored")]

        with caplog.at_level(logging.INFO, logger="src.log.request"):
            await middleware(_scope(headers=headers), _receive, _Collector())

        started = next(r for r in caplog.records if r.getMessage() == "Request started")
        assert started.tenant_id == "tenant-42"
        assert not hasattr(started, "x_other")

    async def test_authorization_and_cookie_are_never_copied(self, caplog):
        settings = LoggingConfig(
            extra_headers={"authorization": "authorization", "cookie": "cookie"}
        )
        middleware = RequestLoggingMiddleware(_ok_app, settings=settings)
        headers = [(b"authorization", b"Bearer secret"), (b"cookie", b"session=abc")]

        with caplog.at_level(logging.INFO, logger="src.log.request"):
            await middleware(_scope(headers=headers), _receive, _Collector())

        started = next(r for r in caplog.records if r.getMessage() == "Request started")
        assert not hasattr(started, "authorization")
        assert not hasattr(started, "cookie")
