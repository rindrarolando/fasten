from unittest.mock import AsyncMock

import httpx
import pytest

from src.auth.dto import Principal
from src.main import app


@pytest.fixture
def client():
    return httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://test"
    )


async def test_missing_bearer(client):
    async with client:
        for path in ["/api/v1/auth/me", "/api/v1/admin/health"]:
            response = await client.get(path)
            assert response.status_code == 401
            assert response.headers["www-authenticate"] == "Bearer"


@pytest.mark.parametrize(
    "roles,status",
    [([], 403), (["USER"], 403), (["ADMIN"], 200), (["SUPERADMIN"], 200)],
)
async def test_role_boundary(client, roles, status):
    service = AsyncMock()
    service.authenticate.return_value = Principal(
        subject="u1", issuer="https://issuer.test", roles=roles
    )
    with app.container.auth.service.override(service):
        async with client:
            response = await client.get(
                "/api/v1/admin/health", headers={"Authorization": "Bearer token"}
            )
            assert response.status_code == status
            me = await client.get(
                "/api/v1/auth/me", headers={"Authorization": "Bearer token"}
            )
            assert me.status_code == 200
            assert me.json()["roles"] == roles


async def test_old_credentials_and_routes_are_gone(client):
    async with client:
        assert (
            await client.post(
                "/auth/admin/login", json={"username": "admin", "password": "test"}
            )
        ).status_code == 404
        assert (await client.get("/auth/admin/users")).status_code == 404
        assert (
            await client.get(
                "/api/v1/auth/me",
                headers={
                    "X-Client-Secret": "test",
                    "X-Admin-Username": "admin",
                    "X-Admin-Password": "test",
                },
            )
        ).status_code == 401
        schema = (await client.get("/openapi.json")).json()
        assert "HTTPBearer" in schema["components"]["securitySchemes"]
        assert (await client.get("/health")).status_code == 200
