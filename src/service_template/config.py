from functools import lru_cache

from src.config import DBConfig


# TODO: rename this class and function to match your service name,
#       e.g. ProductConfig / get_product_config.
class ServiceConfig(DBConfig):
    """Service-specific DB config. Inherits all base DB settings."""


@lru_cache
def get_service_config() -> ServiceConfig:
    return ServiceConfig()
