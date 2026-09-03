import uuid

import bcrypt

from src.auth.config import AuthConfig
from src.auth.dal import AuthDal
from src.auth.dto import AdminUserCreate, AdminUserRead, AdminUserUpdate
from src.auth.enums.enum import AdminUserRole
from src.auth.errors import AdminUserNotFound
from src.log import get_feature_logger, operation_log
from src.utils import paginate

logger = get_feature_logger(__name__, feature="auth")


class AuthService:
    def __init__(self, config: AuthConfig, dal: AuthDal) -> None:
        self._config = config
        self._dal = dal

    @operation_log("verify_client_secret", feature="auth")
    def verify_client_secret(self, secret: str) -> bool:
        return secret == self._config.CLIENT_SHARED_SECRET

    @operation_log("verify_admin_credentials", feature="auth")
    async def verify_admin_credentials(self, username: str, password: str) -> bool:
        user = await self._dal.get_by_username(username)
        if user is None or not user.is_active:
            return False
        return self._verify_password(password, user.password_hash)

    @operation_log("ensure_default_admin", feature="auth")
    async def ensure_default_admin(self) -> None:
        """Seed the bootstrap admin account from ADMIN_USERNAME/ADMIN_PASSWORD
        on first startup. No-op once that account already exists."""
        existing = await self._dal.get_by_username(self._config.ADMIN_USERNAME)
        if existing is not None:
            return
        await self._dal.create(
            {
                "uid": uuid.uuid4(),
                "username": self._config.ADMIN_USERNAME,
                "password_hash": self._hash_password(self._config.ADMIN_PASSWORD),
                "role": AdminUserRole.SUPERADMIN.value,
                "is_active": True,
            }
        )
        logger.info(
            "Default admin user seeded", extra={"username": self._config.ADMIN_USERNAME}
        )

    @operation_log("create_admin_user", feature="auth")
    async def create_admin_user(self, body: AdminUserCreate) -> AdminUserRead:
        obj = await self._dal.create(
            {
                "uid": uuid.uuid4(),
                "username": body.username,
                "password_hash": self._hash_password(body.password),
                "role": body.role.value,
                "is_active": True,
            }
        )
        return AdminUserRead.model_validate(obj)

    @paginate(default_limit=50)
    @operation_log("list_admin_users", feature="auth")
    async def list_admin_users(self, page: int, size: int) -> tuple[list[AdminUserRead], int]:
        items, total = await self._dal.list(page, size)
        return [AdminUserRead.model_validate(i) for i in items], total

    @operation_log("get_admin_user", feature="auth")
    async def get_admin_user(self, uid: uuid.UUID) -> AdminUserRead:
        obj = await self._dal.get_by_uid(uid)
        if obj is None:
            raise AdminUserNotFound(str(uid))
        return AdminUserRead.model_validate(obj)

    @operation_log("update_admin_user", feature="auth")
    async def update_admin_user(self, uid: uuid.UUID, body: AdminUserUpdate) -> AdminUserRead:
        obj = await self._dal.get_by_uid(uid)
        if obj is None:
            raise AdminUserNotFound(str(uid))
        updates = body.model_dump(exclude_none=True, exclude={"password", "role"})
        if body.password is not None:
            updates["password_hash"] = self._hash_password(body.password)
        if body.role is not None:
            updates["role"] = body.role.value
        updated = await self._dal.update(obj.id, updates)
        return AdminUserRead.model_validate(updated)

    @operation_log("delete_admin_user", feature="auth")
    async def delete_admin_user(self, uid: uuid.UUID) -> None:
        obj = await self._dal.get_by_uid(uid)
        if obj is None:
            raise AdminUserNotFound(str(uid))
        await self._dal.delete(obj.id)

    @staticmethod
    def _hash_password(password: str) -> str:
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    @staticmethod
    def _verify_password(password: str, password_hash: str) -> bool:
        return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))
