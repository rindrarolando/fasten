"""Real PostgreSQL integration test, enabled by TEST_DATABASE_URL (dedicated disposable DB)."""

import os
import subprocess
import uuid
from pathlib import Path

import pytest
from alembic.autogenerate import compare_metadata
from alembic.migration import MigrationContext

from src.async_database import AsyncDatabase
from src.config import Settings
from src.models import Base
from src.service_template.container import ServiceContainer


@pytest.mark.skipif(
    not os.getenv("TEST_DATABASE_URL"), reason="TEST_DATABASE_URL not set"
)
async def test_migrations_and_shared_database():
    env = dict(os.environ, DATABASE_URL=os.environ["TEST_DATABASE_URL"])
    env.pop("DATABASE_HOST_OVERRIDE", None)
    root = Path(__file__).resolve().parents[1]

    def alembic(*args):
        subprocess.run(
            [str(Path(os.sys.executable).parent / "alembic"), *args],
            cwd=root,
            env=env,
            check=True,
        )

    alembic("upgrade", "head")
    db = AsyncDatabase(
        Settings(
            DATABASE_URL=env["DATABASE_URL"], DATABASE_HOST_OVERRIDE=None
        ).database_url
    )
    try:
        from fastapi import HTTPException
        from sqlalchemy import update

        from src.auth.config import AuthConfig
        from src.auth.dal import UserDal
        from src.auth.dto import RegisterRequest
        from src.auth.local import LocalAuthService
        from src.auth.models import User

        auth = LocalAuthService(
            AuthConfig(
                AUTH_MODE="local",
                JWT_SECRET_KEY="integration-test-secret-at-least-32-characters",
            ),
            UserDal(db),
        )
        body = RegisterRequest(
            email="integration@example.com", password="strong-test-password"
        )
        principal = await auth.create_user(body)
        token = (await auth.login(body)).access_token
        assert (await auth.authenticate(token)).roles == ["USER"]
        with pytest.raises(HTTPException) as conflict:
            await auth.create_user(body)
        assert conflict.value.status_code == 409
        async with db.session() as session:
            await session.execute(
                update(User)
                .where(User.uid == uuid.UUID(principal.subject))
                .values(is_active=False)
            )
            await session.commit()
        with pytest.raises(HTTPException) as inactive:
            await auth.authenticate(token)
        assert inactive.value.status_code == 401
        domain = ServiceContainer(db=db)
        assert domain.db() is db
        uid = uuid.uuid4()
        created = await domain.dal().create(
            {"uid": uid, "name": "postgres", "meta": {"test": True}}
        )
        assert created.uid == uid
        assert created.created_at.tzinfo is not None
        updated = await domain.dal().update(created.id, {"name": "updated"})
        assert updated.name == "updated"
        assert updated.updated_at.tzinfo is not None
        async with db.engine.connect() as connection:
            diff = await connection.run_sync(
                lambda c: compare_metadata(MigrationContext.configure(c), Base.metadata)
            )
        assert diff == []
        await domain.dal().delete(created.id)
        assert await domain.dal().get_by_uid(uid) is None
    finally:
        await db.disconnect()
    alembic("downgrade", "base")
    alembic("upgrade", "head")
