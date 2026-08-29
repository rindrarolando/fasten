import io
import json
import logging

from src.log.setup import setup_logging


class TestSetupLogging:
    def test_configures_a_single_json_stdout_handler(self):
        root = logging.getLogger()
        original_handlers = list(root.handlers)
        try:
            setup_logging(level="DEBUG")
            assert root.level == logging.DEBUG
            assert len(root.handlers) == 1
        finally:
            root.handlers = original_handlers

    def test_reconfiguring_does_not_duplicate_handlers(self):
        root = logging.getLogger()
        original_handlers = list(root.handlers)
        try:
            setup_logging(level="INFO")
            setup_logging(level="INFO")
            assert len(root.handlers) == 1
        finally:
            root.handlers = original_handlers

    def test_emits_one_json_line_per_record(self):
        root = logging.getLogger()
        original_handlers = list(root.handlers)
        try:
            setup_logging(level="INFO")
            stream = io.StringIO()
            root.handlers[0].stream = stream
            logging.getLogger("test.setup").info("hello")
            line = stream.getvalue().strip()
            payload = json.loads(line)
            assert payload["message"] == "hello"
        finally:
            root.handlers = original_handlers
