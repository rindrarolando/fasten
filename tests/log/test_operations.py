import logging

import pytest

from src.log.operations import operation_log, operation_logger


class TestOperationLogAsync:
    async def test_success_logs_start_and_complete(self, caplog):
        @operation_log("create_order", feature="orders")
        async def create_order(value: int) -> int:
            return value * 2

        with caplog.at_level(logging.INFO):
            result = await create_order(21)

        assert result == 42
        messages = [r.getMessage() for r in caplog.records]
        assert any(m.startswith("Starting operation: create_order") for m in messages)
        completed = next(r for r in caplog.records if r.getMessage().startswith("Completed operation"))
        assert completed.operation == "create_order"
        assert completed.feature == "orders"
        assert completed.duration_ms >= 0
        assert completed.name == create_order.__module__  # logger bound to wrapped module

    async def test_failure_logs_error_and_reraises(self, caplog):
        @operation_log("create_order", feature="orders")
        async def create_order() -> None:
            raise ValueError("boom")

        with caplog.at_level(logging.INFO):
            with pytest.raises(ValueError, match="boom"):
                await create_order()

        failed = next(r for r in caplog.records if r.getMessage().startswith("Failed operation"))
        assert failed.error == "boom"
        assert failed.error_type == "ValueError"
        assert failed.exc_info is not None


class TestOperationLogSync:
    def test_success_same_contract_as_async(self, caplog):
        @operation_log("verify_secret", feature="auth")
        def verify_secret(secret: str) -> bool:
            return secret == "shh"

        with caplog.at_level(logging.INFO):
            assert verify_secret("shh") is True

        messages = [r.getMessage() for r in caplog.records]
        assert any(m.startswith("Starting operation: verify_secret") for m in messages)
        assert any(m.startswith("Completed operation: verify_secret") for m in messages)


class TestOperationLoggerContextManager:
    def test_wraps_a_block_not_a_function(self, caplog):
        with caplog.at_level(logging.INFO):
            with operation_logger("batch_step", feature="workers"):
                pass

        messages = [r.getMessage() for r in caplog.records]
        assert any(m.startswith("Starting operation: batch_step") for m in messages)
        assert any(m.startswith("Completed operation: batch_step") for m in messages)
