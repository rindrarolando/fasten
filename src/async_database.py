from sqlalchemy import MetaData, text
from sqlalchemy.engine import URL
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    metadata = MetaData(
        naming_convention={
            "ix": "ix_%(column_0_label)s",
            "uq": "uq_%(table_name)s_%(column_0_name)s",
            "ck": "ck_%(table_name)s_%(constraint_name)s",
            "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
            "pk": "pk_%(table_name)s",
        }
    )


class AsyncDatabase:
    """One engine/session factory shared by every domain in this process."""

    def __init__(self, url: URL, echo: bool = False) -> None:
        self.engine = create_async_engine(
            url, echo=echo, pool_pre_ping=True, hide_parameters=True
        )
        self._sessions = async_sessionmaker(self.engine, expire_on_commit=False)

    def session(self) -> AsyncSession:
        return self._sessions()

    async def check(self) -> None:
        async with self.engine.connect() as connection:
            await connection.execute(text("SELECT 1"))

    async def disconnect(self) -> None:
        await self.engine.dispose()
