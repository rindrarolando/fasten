import json
import logging

from src.log.context import reset_request_id, set_request_id
from src.log.formatter import JsonFormatter


def _make_record(**extra) -> logging.LogRecord:
    record = logging.LogRecord(
        name="src.orders.service",
        level=logging.INFO,
        pathname=__file__,
        lineno=42,
        msg="Created order",
        args=(),
        exc_info=None,
        func="create_order",
    )
    for key, value in extra.items():
        setattr(record, key, value)
    return record


class TestJsonFormatter:
    def test_emits_valid_json_with_base_fields(self):
        payload = json.loads(JsonFormatter().format(_make_record()))
        assert payload["level"] == "INFO"
        assert payload["module"] == "src.orders.service"
        assert payload["function"] == "create_order"
        assert payload["line"] == 42
        assert payload["message"] == "Created order"
        # ISO-8601 with an explicit UTC offset.
        assert payload["timestamp"].endswith("+00:00")

    def test_omits_request_id_when_unset(self):
        payload = json.loads(JsonFormatter().format(_make_record()))
        assert "request_id" not in payload

    def test_includes_request_id_when_set(self):
        token = set_request_id("req-1")
        try:
            payload = json.loads(JsonFormatter().format(_make_record()))
        finally:
            reset_request_id(token)
        assert payload["request_id"] == "req-1"

    def test_includes_extra_fields(self):
        record = _make_record(feature="orders", operation="create_order", duration_ms=12.3)
        payload = json.loads(JsonFormatter().format(record))
        assert payload["feature"] == "orders"
        assert payload["operation"] == "create_order"
        assert payload["duration_ms"] == 12.3

    def test_serializes_non_json_native_extras(self):
        import uuid

        record = _make_record(order_id=uuid.UUID(int=0))
        payload = json.loads(JsonFormatter().format(record))
        assert payload["order_id"] == str(uuid.UUID(int=0))
