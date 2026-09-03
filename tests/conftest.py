"""Shared fixtures for unit tests."""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from src.auth.config import AuthConfig
from src.auth.service import AuthService


@pytest.fixture
def auth_config() -> AuthConfig:
    return AuthConfig(
        CLIENT_SHARED_SECRET="test-secret",
        ADMIN_USERNAME="admin",
        ADMIN_PASSWORD="admin-pass",
    )


@pytest.fixture
def auth_dal() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def auth_service(auth_config: AuthConfig, auth_dal: AsyncMock) -> AuthService:
    return AuthService(auth_config, auth_dal)
