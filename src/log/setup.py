import logging
import sys

from src.log.formatter import JsonFormatter


def setup_logging(level: str = "INFO") -> None:
    """
    Configure the root logger for JSON-on-stdout. Call once at process start
    (ASGI entrypoint, worker/CLI entrypoint). Replaces any existing root
    handlers so it is safe to call again under `uvicorn --reload`.
    """
    root = logging.getLogger()
    root.setLevel(level.upper())
    root.handlers.clear()

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())
    root.addHandler(handler)

    logging.captureWarnings(True)
