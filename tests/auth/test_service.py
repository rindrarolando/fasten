import time
from unittest.mock import Mock

import httpx
import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi import HTTPException

from src.auth.config import AuthConfig
from src.auth.service import AuthService

JWKS_FETCH_DATA = jwt.PyJWKClient.fetch_data


@pytest.fixture
def provider(monkeypatch):
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public = jwt.algorithms.RSAAlgorithm.to_jwk(key.public_key(), as_dict=True)
    public.update(kid="key-1", alg="RS256", use="sig")
    discovery = Mock(
        return_value=httpx.Response(
            200,
            json={
                "issuer": "https://issuer.test",
                "jwks_uri": "https://issuer.test/keys",
            },
            request=httpx.Request("GET", "https://issuer.test"),
        )
    )
    monkeypatch.setattr(httpx, "get", discovery)
    monkeypatch.setattr(jwt.PyJWKClient, "fetch_data", lambda self: {"keys": [public]})
    service = AuthService(
        AuthConfig(
            AUTH_MODE="oidc",
            OIDC_ISSUER="https://issuer.test",
            OIDC_AUDIENCE="fasten-api",
        )
    )

    def token(**changes):
        claims = dict(
            sub="user-1",
            iss="https://issuer.test",
            aud="fasten-api",
            exp=int(time.time()) + 300,
            iat=int(time.time()),
            roles=["ADMIN"],
        )
        claims.update(changes)
        return jwt.encode(claims, key, algorithm="RS256", headers={"kid": "key-1"})

    return service, token, discovery, key


async def test_signed_token_and_cached_discovery(provider):
    service, token, discovery, _ = provider
    assert (await service.authenticate(token())).roles == ["ADMIN"]
    await service.authenticate(token())
    discovery.assert_called_once()


@pytest.mark.parametrize(
    "changes",
    [
        {"iss": "https://attacker.test"},
        {"aud": "frontend-client"},
        {"exp": 1},
        {"sub": ""},
        {"sub": None},
        {"iat": int(time.time()) + 3600},
        {"nbf": int(time.time()) + 3600},
        {"roles": "SUPERADMIN"},
    ],
)
async def test_invalid_claims(provider, changes):
    service, token, _, _ = provider
    with pytest.raises(HTTPException) as error:
        await service.authenticate(token(**changes))
    assert error.value.status_code == 401


@pytest.mark.parametrize("claim", ["exp", "iat", "iss", "aud", "sub"])
async def test_required_claims(provider, claim):
    service, token, _, key = provider
    claims = jwt.decode(token(), options={"verify_signature": False})
    del claims[claim]
    encoded = jwt.encode(claims, key, algorithm="RS256", headers={"kid": "key-1"})
    with pytest.raises(HTTPException) as error:
        await service.authenticate(encoded)
    assert error.value.status_code == 401


async def test_signature_and_algorithm_rejected(provider):
    service, token, _, _ = provider
    other = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    claims = jwt.decode(token(), options={"verify_signature": False})
    for encoded in [
        jwt.encode(claims, other, algorithm="RS256", headers={"kid": "key-1"}),
        jwt.encode(
            claims,
            "a-long-enough-untrusted-secret-value",
            algorithm="HS256",
            headers={"kid": "key-1"},
        ),
        "not.a.jwt",
    ]:
        with pytest.raises(HTTPException) as error:
            await service.authenticate(encoded)
        assert error.value.status_code == 401


async def test_nested_roles_and_unknown_key(provider):
    service, token, _, _ = provider
    service._config.OIDC_ROLES_CLAIM = "realm_access.roles"
    assert (
        await service.authenticate(token(realm_access={"roles": ["SUPERADMIN"]}))
    ).roles == ["SUPERADMIN"]
    assert (await service.authenticate(token())).roles == []
    encoded = token().split(".")
    import json

    encoded[0] = jwt.utils.base64url_encode(
        json.dumps({"alg": "RS256", "kid": "unknown"}).encode()
    ).decode()
    with pytest.raises(HTTPException) as error:
        await service.authenticate(".".join(encoded))
    assert error.value.status_code == 401


async def test_provider_failure_is_503(provider, monkeypatch):
    service, token, discovery, _ = provider
    discovery.side_effect = httpx.ConnectError("unavailable")
    with pytest.raises(HTTPException) as error:
        await service.authenticate(token())
    assert error.value.status_code == 503


async def test_discovery_issuer_must_match(provider):
    service, token, discovery, _ = provider
    discovery.return_value = httpx.Response(
        200,
        json={"issuer": "https://evil.test", "jwks_uri": "https://evil.test/keys"},
        request=httpx.Request("GET", "https://issuer.test"),
    )
    with pytest.raises(HTTPException) as error:
        await service.authenticate(token())
    assert error.value.status_code == 503


def test_https_required():
    with pytest.raises(ValueError):
        AuthConfig(
            AUTH_MODE="oidc", OIDC_ISSUER="http://issuer.test", OIDC_AUDIENCE="api"
        )


async def test_rotated_signing_key_is_refreshed(provider, monkeypatch):
    service, token, _, key = provider
    # Use the real JWKS fetch/cache implementation against a mocked HTTP response.
    import io
    import json
    import urllib.request

    rotated = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    responses = []
    for kid, signing_key in [("key-1", key), ("key-2", rotated)]:
        jwk = jwt.algorithms.RSAAlgorithm.to_jwk(signing_key.public_key(), as_dict=True)
        jwk.update(kid=kid, alg="RS256", use="sig")
        responses.append(json.dumps({"keys": [jwk]}).encode())
    monkeypatch.setattr(jwt.PyJWKClient, "fetch_data", JWKS_FETCH_DATA)

    def urlopen(*args, **kwargs):
        return io.BytesIO(responses.pop(0))

    monkeypatch.setattr(
        urllib.request, "build_opener", lambda *args: Mock(open=urlopen)
    )
    assert (await service.authenticate(token())).subject == "user-1"
    # Simulate the provider-refresh cooldown having elapsed.
    service._jwks._last_successful_fetch = None
    claims = jwt.decode(token(), options={"verify_signature": False})
    rotated_token = jwt.encode(
        claims, rotated, algorithm="RS256", headers={"kid": "key-2"}
    )
    assert (await service.authenticate(rotated_token)).subject == "user-1"
    assert not responses
