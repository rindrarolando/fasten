from types import SimpleNamespace
from unittest.mock import AsyncMock

import bcrypt

from src.auth.service import AuthService


def _hash(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


class TestVerifyClientSecret:
    def test_returns_true_for_matching_secret(self, auth_service: AuthService):
        assert auth_service.verify_client_secret("test-secret") is True

    def test_returns_false_for_wrong_secret(self, auth_service: AuthService):
        assert auth_service.verify_client_secret("wrong") is False

    def test_returns_false_for_empty_secret(self, auth_service: AuthService):
        assert auth_service.verify_client_secret("") is False


class TestVerifyAdminCredentials:
    async def test_returns_true_for_valid_credentials(
        self, auth_service: AuthService, auth_dal: AsyncMock
    ):
        auth_dal.get_by_username.return_value = SimpleNamespace(
            password_hash=_hash("admin-pass"), is_active=True
        )
        assert await auth_service.verify_admin_credentials("admin", "admin-pass") is True

    async def test_returns_false_for_wrong_username(
        self, auth_service: AuthService, auth_dal: AsyncMock
    ):
        auth_dal.get_by_username.return_value = None
        assert await auth_service.verify_admin_credentials("other", "admin-pass") is False

    async def test_returns_false_for_wrong_password(
        self, auth_service: AuthService, auth_dal: AsyncMock
    ):
        auth_dal.get_by_username.return_value = SimpleNamespace(
            password_hash=_hash("admin-pass"), is_active=True
        )
        assert await auth_service.verify_admin_credentials("admin", "wrong") is False

    async def test_returns_false_for_inactive_user(
        self, auth_service: AuthService, auth_dal: AsyncMock
    ):
        auth_dal.get_by_username.return_value = SimpleNamespace(
            password_hash=_hash("admin-pass"), is_active=False
        )
        assert await auth_service.verify_admin_credentials("admin", "admin-pass") is False


class TestEnsureDefaultAdmin:
    async def test_creates_when_missing(self, auth_service: AuthService, auth_dal: AsyncMock):
        auth_dal.get_by_username.return_value = None
        await auth_service.ensure_default_admin()
        auth_dal.create.assert_called_once()

    async def test_skips_when_already_exists(
        self, auth_service: AuthService, auth_dal: AsyncMock
    ):
        auth_dal.get_by_username.return_value = SimpleNamespace()
        await auth_service.ensure_default_admin()
        auth_dal.create.assert_not_called()
