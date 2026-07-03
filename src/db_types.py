import uuid
from typing import Optional

from sqlalchemy import CHAR
from sqlalchemy.types import TypeDecorator


class FormattedUUID(TypeDecorator):
    """Platform-independent UUID type that stores UUIDs without dashes (CHAR(32) hex).

    Python side : uuid.UUID
    DB side     : CHAR(32) hex string, e.g. "550e8400e29b41d4a716446655440000"
    JSON side   : standard dashed form, e.g. "550e8400-e29b-41d4-a716-446655440000"
    """

    impl = CHAR
    cache_ok = True

    def __init__(self) -> None:
        super().__init__(length=32)

    def process_bind_param(
        self, value: Optional[uuid.UUID], dialect
    ) -> Optional[str]:
        if value is None:
            return None
        return value.hex

    def process_result_value(
        self, value: Optional[str], dialect
    ) -> Optional[uuid.UUID]:
        if value is None:
            return None
        return uuid.UUID(value)

    def process_literal_param(
        self, value: Optional[uuid.UUID], dialect
    ) -> Optional[str]:
        if value is None:
            return None
        return f"'{value.hex}'" if isinstance(value, uuid.UUID) else f"'{value}'"
