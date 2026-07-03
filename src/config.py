from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class DBConfig(BaseSettings):
    """
    Base database configuration shared across all services.

    Convention:
      - db name    : <service_name>_db
      - db user    : <service_name>_user
      - db password: shared default (overridable per service)
      - host/port  : shared, single DB instance
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Async SQLAlchemy driver string — swap to match your database:
    #   mysql+aiomysql       (MySQL / MariaDB)
    #   postgresql+asyncpg   (PostgreSQL)
    #   sqlite+aiosqlite     (SQLite, dev/test only)
    DB_DRIVER: str = "mysql+aiomysql"

    DB_HOST: str = "0.0.0.0"
    DB_PORT: int = 3306

    DB_DEFAULT_PASSWORD: str = "test1234"

    DB_ECHO: bool = False
    DB_CONN_ECHO: bool = False

    def db_url(self, service_name: str, password: str | None = None) -> str:
        """
        Build an async DB URL for the given service.

        service_name examples: "auth", "product"
          -> product: mysql+aiomysql://product_user:test1234@0.0.0.0:3306/product_db
        """
        db_name = f"{service_name}_db"
        db_user = f"{service_name}_user"
        db_password = password or self.DB_DEFAULT_PASSWORD
        return (
            f"{self.DB_DRIVER}://{db_user}:{db_password}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{db_name}"
        )


@lru_cache
def get_db_config() -> DBConfig:
    return DBConfig()
