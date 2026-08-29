import logging
from typing import Any, MutableMapping


class FeatureLogger(logging.LoggerAdapter):
    """LoggerAdapter that always tags log lines with `feature`."""

    def process(
        self, msg: Any, kwargs: MutableMapping[str, Any]
    ) -> tuple[Any, MutableMapping[str, Any]]:
        extra = dict(kwargs.get("extra") or {})
        extra.setdefault("feature", self.extra["feature"])
        kwargs["extra"] = extra
        return msg, kwargs


def get_feature_logger(name: str, *, feature: str) -> FeatureLogger:
    """
    logger = get_feature_logger(__name__, feature="auth")
    logger.info("...", extra={"user_id": "..."})
    """
    return FeatureLogger(logging.getLogger(name), {"feature": feature})
