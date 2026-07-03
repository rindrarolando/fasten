from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Shared declarative base for all SQLAlchemy models."""


class AsyncDatabase:
    """
    Manages an async SQLAlchemy engine and session factory for one service DB.

    Usage (wired via dependency-injector):
        db = AsyncDatabase(url="mysql+aiomysql://...", echo=False)
        await db.connect()
        ...
        await db.disconnect()

    Session usage inside a route/service:
        async with db.session() as session:
            ...
    """

    def __init__(self, url: str, echo: bool = False, echo_pool: bool = False) -> None:
        self._url = url
        self._echo = echo
        self._echo_pool = echo_pool
        self._engine: AsyncEngine | None = None
        self._session_factory: async_sessionmaker[AsyncSession] | None = None

    async def connect(self) -> None:
        self._engine = create_async_engine(
            self._url,
            echo=self._echo,
            echo_pool=self._echo_pool,
            pool_pre_ping=True,
        )
        self._session_factory = async_sessionmaker(
            self._engine,
            expire_on_commit=False,
            class_=AsyncSession,
        )

    async def disconnect(self) -> None:
        if self._engine:
            await self._engine.dispose()
            self._engine = None
            self._session_factory = None

    def session(self) -> AsyncGenerator[AsyncSession, None]:
        if self._session_factory is None:
            raise RuntimeError("Database not connected. Call connect() first.")
        return self._session_factory()
