import uuid
from unittest.mock import AsyncMock

import httpx
import jwt
import pytest
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError

from src.auth.config import AuthConfig
from src.auth.dto import Credentials, RegisterRequest
from src.auth.local import LocalAuthService
from src.main import app


@pytest.fixture
def local():
    config = AuthConfig(
        AUTH_MODE="local",
        JWT_SECRET_KEY="test-secret-that-is-at-least-32-characters",
        AUTH_ALLOW_REGISTRATION=True,
    )
    dal = AsyncMock()
    dal.create.side_effect = lambda user: user
    return LocalAuthService(config, dal), dal


async def test_register_login_and_live_roles(local):
    service, dal = local
    body = RegisterRequest(email="You@Example.com", password="strong-test-password")
    principal = await service.create_user(body)
    user = dal.create.call_args.args[0]
    assert user.email == "you@example.com"
    assert user.password_hash.startswith("$argon2id$")
    assert "strong-test-password" not in user.password_hash
    assert principal.roles == ["USER"]
    dal.get_by_email.return_value = user
    dal.get_by_uid.return_value = user
    token = (await service.login(body)).access_token
    assert (await service.authenticate(token)).subject == str(user.uid)
    user.role = "ADMIN"
    assert (await service.authenticate(token)).roles == ["ADMIN"]
    user.is_active = False
    with pytest.raises(HTTPException) as error:
        await service.authenticate(token)
    assert error.value.status_code == 401
    with pytest.raises(HTTPException):
        await service.login(body)


async def test_invalid_credentials_and_duplicate(local):
    service, dal = local
    body = RegisterRequest(email="you@example.com", password="strong-test-password")
    await service.create_user(body)
    user = dal.create.call_args.args[0]
    dal.get_by_email.return_value = user
    with pytest.raises(HTTPException) as error:
        await service.login(Credentials(email=body.email, password="wrong-password"))
    assert error.value.status_code == 401
    dal.get_by_email.return_value = None
    with pytest.raises(HTTPException) as error:
        await service.login(body)
    assert error.value.status_code == 401
    dal.create.side_effect = IntegrityError("insert", {}, Exception("duplicate"))
    with pytest.raises(HTTPException) as error:
        await service.create_user(body)
    assert error.value.status_code == 409


@pytest.mark.parametrize(
    "changes", [{"exp": 1}, {"aud": "other"}, {"iss": "other"}, {"sub": "bad-uuid"}]
)
async def test_invalid_local_tokens(local, changes):
    service, dal = local
    claims = dict(
        sub=str(uuid.uuid4()),
        iss=service.config.JWT_ISSUER,
        aud=service.config.JWT_AUDIENCE,
        iat=1,
        exp=9999999999,
    )
    claims.update(changes)
    token = jwt.encode(
        claims, service.config.JWT_SECRET_KEY.get_secret_value(), algorithm="HS256"
    )
    with pytest.raises(HTTPException) as error:
        await service.authenticate(token)
    assert error.value.status_code == 401
    dal.get_by_uid.assert_not_called()


async def test_local_http_flow_and_no_role_injection(local):
    service, dal = local

    async def create(user):
        dal.get_by_email.return_value = user
        dal.get_by_uid.return_value = user
        return user

    dal.create.side_effect = create
    with app.container.auth.service.override(service):
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://test"
        ) as client:
            body = {"email": "you@example.com", "password": "strong-test-password"}
            assert (
                await client.post(
                    "/api/v1/auth/register", json={**body, "role": "SUPERADMIN"}
                )
            ).status_code == 422
            assert (
                await client.post("/api/v1/auth/register", json=body)
            ).status_code == 201
            response = await client.post("/api/v1/auth/login", json=body)
            assert response.status_code == 200
            headers = {"Authorization": "Bearer " + response.json()["access_token"]}
            assert (await client.get("/api/v1/auth/me", headers=headers)).json()[
                "roles"
            ] == ["USER"]
            assert (
                await client.get("/api/v1/admin/health", headers=headers)
            ).status_code == 403
            service.config.AUTH_ALLOW_REGISTRATION = False
            assert (
                await client.post("/api/v1/auth/register", json=body)
            ).status_code == 404


def test_configuration_modes():
    with pytest.raises(ValueError):
        AuthConfig(AUTH_MODE="local", JWT_SECRET_KEY="short")
    with pytest.raises(ValueError):
        AuthConfig(AUTH_MODE="oidc", OIDC_ISSUER=None, OIDC_AUDIENCE=None)
