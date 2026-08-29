import logging

from src.log.logger import get_feature_logger


class TestFeatureLogger:
    def test_sets_feature_when_extra_omitted(self, caplog):
        logger = get_feature_logger("test.feature.logger", feature="orders")
        with caplog.at_level(logging.INFO, logger="test.feature.logger"):
            logger.info("Created order")
        assert caplog.records[0].feature == "orders"

    def test_does_not_override_explicit_feature(self, caplog):
        logger = get_feature_logger("test.feature.logger.override", feature="orders")
        with caplog.at_level(logging.INFO, logger="test.feature.logger.override"):
            logger.info("Created order", extra={"feature": "billing"})
        assert caplog.records[0].feature == "billing"

    def test_preserves_other_extras(self, caplog):
        logger = get_feature_logger("test.feature.logger.extras", feature="orders")
        with caplog.at_level(logging.INFO, logger="test.feature.logger.extras"):
            logger.info("Created order", extra={"order_id": "o1"})
        record = caplog.records[0]
        assert record.order_id == "o1"
        assert record.feature == "orders"
