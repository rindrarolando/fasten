import pytest

from src.config import Settings


def test_postgres_url_preserves_escaped_password():
    settings = Settings(
        DATABASE_URL="postgresql://user:abc%40def@localhost:5432/app",
        DATABASE_HOST_OVERRIDE="db",
    )
    assert settings.database_url.drivername == "postgresql+asyncpg"
    assert settings.database_url.password == "abc@def"
    assert settings.database_url.host == "db"


def test_non_postgres_rejected():
    with pytest.raises(ValueError):
        Settings(DATABASE_URL="mysql://user:pass@localhost/app")
