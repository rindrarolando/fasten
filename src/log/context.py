from __future__ import annotations

import contextvars
from typing import Any

_request_id: contextvars.ContextVar[str | None] = contextvars.ContextVar(
    "request_id", default=None
)
_log_context: contextvars.ContextVar[dict[str, Any]] = contextvars.ContextVar(
    "log_context", default={}
)


def set_request_id(request_id: str | None) -> contextvars.Token:
    return _request_id.set(request_id)


def get_request_id() -> str | None:
    return _request_id.get()


def reset_request_id(token: contextvars.Token) -> None:
    _request_id.reset(token)


def get_log_context() -> dict[str, Any]:
    return dict(_log_context.get())


def bind_log_context(**kwargs: Any) -> contextvars.Token:
    """
    Merge kwargs onto the ambient log context. Nestable: reset the returned
    token to restore the previous dict (e.g. `_log_context.reset(token)`).
    """
    current = _log_context.get()
    return _log_context.set({**current, **kwargs})


def reset_log_context(token: contextvars.Token) -> None:
    _log_context.reset(token)
