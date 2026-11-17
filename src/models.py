"""Import every persisted model here so Alembic sees the complete metadata."""

from src.async_database import Base
from src.service_template.models.example import ExampleModel

__all__ = ["Base", "ExampleModel"]
