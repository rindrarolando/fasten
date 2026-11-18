import uuid

from sqlalchemy import select

from src.async_database import AsyncDatabase
from src.auth.models import User


class UserDal:
    def __init__(self, db: AsyncDatabase):
        self.db = db

    async def get_by_email(self, email: str) -> User | None:
        async with self.db.session() as session:
            return await session.scalar(select(User).where(User.email == email))

    async def get_by_uid(self, uid: uuid.UUID) -> User | None:
        async with self.db.session() as session:
            return await session.get(User, uid)

    async def create(self, user: User) -> User:
        async with self.db.session() as session:
            session.add(user)
            await session.commit()
            await session.refresh(user)
            return user
