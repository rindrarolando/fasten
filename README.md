# Fasten

Async FastAPI backend with one PostgreSQL database, Alembic migrations, built-in email/password login, JWT access tokens and role-based authorization (with optional OIDC). Inspired by the [FastAPI full-stack template](https://github.com/fastapi/full-stack-fastapi-template), retaining this project's async SQLAlchemy and dependency-injector service layers.

## Requirements and setup

- Python 3.12+, PostgreSQL 17 (or Docker Compose)
- No external identity provider is needed for the default email/password mode.

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.lock
cp .env.example .env
```

Edit `.env`: choose a strong PostgreSQL password, update `DATABASE_URL` to match, and set `JWT_SECRET_KEY` to a random value generated with `openssl rand -hex 32`. Percent-encode special characters in the URL password (`@` becomes `%40`). PostgreSQL's `POSTGRES_PASSWORD` remains the raw password. `DATABASE_URL` is required; there are no built-in database or administrator credentials.

For a host-run API:

```sh
docker compose up -d db
alembic upgrade head
uvicorn src.main:app --reload
```

For the container stack:

```sh
docker compose up --build
```

Compose starts PostgreSQL, runs Alembic in a one-shot migration service, then starts the API only if migration succeeds. All domains use the same database. `DATABASE_HOST_OVERRIDE=db` selects the Compose hostname without reconstructing the password-bearing URL. No SQL initialization directory is mounted. Persistent PostgreSQL data uses a named volume. Keep the database private and terminate HTTPS at your deployment ingress.

## Email/password login (default)

Set `AUTH_MODE=local` and generate a unique `JWT_SECRET_KEY` (at least 32 characters). Run `alembic upgrade head` to add the local account table. No identity provider is needed.

Create your first administrator explicitly; there is no default account or password:

```sh
python -m src.auth.manage --email admin@example.com --role SUPERADMIN
# Or inside the Compose API container:
docker compose exec api python -m src.auth.manage --email admin@example.com --role SUPERADMIN
```

The command prompts for a 12–128 character password and confirmation. It also creates ordinary users (`--role USER`) or admins (`--role ADMIN`). Do not put passwords into shell command arguments.

Login accepts JSON:

```sh
curl http://localhost:8000/api/v1/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"admin@example.com","password":"your-password"}'
```

The response contains `access_token` and `token_type: bearer`. Send the token as `Authorization: Bearer <access_token>` for `/api/v1/auth/me` and protected routes. Tokens expire after `ACCESS_TOKEN_EXPIRE_MINUTES` (30 by default); log in again after expiration. There is no refresh-token endpoint. Client logout discards the token; it remains valid until expiry unless its account is disabled or deleted. Keep the signing secret private; rotating it invalidates all local tokens.

Passwords are hashed with Argon2id; hashing and verification run off the event loop. Email addresses are validated and normalized to lowercase. Every authenticated request reloads the account so disabled accounts and role changes take effect immediately. Public requests cannot choose roles. This baseline has no password-reset/email-verification flows; accounts are created through the management command by default. Configure ingress rate limits and HTTPS before public deployment.

Optional self-registration: set `AUTH_ALLOW_REGISTRATION=true` and POST the same email/password JSON to `/api/v1/auth/register`. It always creates a `USER`; a role field is rejected. Registration is disabled by default. Passwords are never returned in responses.

## Optional OIDC and roles

To delegate identity management later, set `AUTH_MODE=oidc`, `OIDC_ISSUER`, `OIDC_AUDIENCE`, and `OIDC_ROLES_CLAIM`. Local login and registration are disabled in that mode. The two modes deliberately do not accept each other's tokens. Local accounts are not automatically linked to provider identities.


In OIDC mode, this backend is a resource server. The identity provider owns login, logout, passwords, MFA, users and role assignment. Local login and registration are disabled; provider identities do not use the local password table. Browser clients use Authorization Code + PKCE through the provider; backend/service clients use a provider-supported flow. Send the resulting **access token** to this API:

```sh
curl http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

Configuration:

- `OIDC_ISSUER`: exact issuer, including any trailing slash, from the provider's discovery document. Discovery uses `<issuer>/.well-known/openid-configuration`.
- `OIDC_AUDIENCE`: dedicated API resource identifier, distinct from the frontend application's client ID. Configure the provider to include it in access tokens. Do not use ID tokens as API credentials.
- `OIDC_ROLES_CLAIM`: path to an array of role strings, default `roles`. Keycloak commonly uses `realm_access.roles`; a namespaced claim is also supported as a literal key (see implementation).
- `OIDC_ALLOW_INSECURE_HTTP`: false by default. Enable only for a local HTTP provider. Containers must reach the issuer at the exact issuer URL; `localhost` inside the API container is not the host machine.
- `OIDC_JWKS_CACHE_SECONDS`: signing-key cache lifetime (default 300 seconds). Unknown key IDs trigger a JWKS refresh for rotation.

Validation restricts the algorithm to RS256, verifies the signature against provider-discovered JWKS, verifies issuer/audience, and requires `exp`, `iat` and `sub`. Expiration and not-before claims are enforced. Roles come only from verified claims. Missing/invalid credentials return 401 with a Bearer challenge; insufficient roles return 403; provider discovery/network failures return 503. Provider IO and token validation execute outside the event loop. No tokens are logged.

Role checks use exact names and explicit allowed roles, without an implicit role hierarchy. `/api/v1/admin/health` accepts `ADMIN` or `SUPERADMIN`. Assign these roles in your provider, and ensure ordinary users cannot edit their own role claims. In OIDC mode, role changes and revocation take effect as access tokens expire; configure suitably short token lifetimes. Configure rate limits at the ingress, including for authentication/JWKS refresh abuse.

For Keycloak: create a realm, register a public frontend client with PKCE S256 and exact redirect URLs, configure an audience mapper for `fasten-api`, create realm roles `ADMIN`/`SUPERADMIN`, assign them to selected users, and set `OIDC_ROLES_CLAIM=realm_access.roles`. The API does not need the frontend's client secret.

## API

- `GET /health`: public process liveness
- `GET /ready`: public database readiness (503 if PostgreSQL is unavailable)
- `POST /api/v1/auth/login`: email/password login in local mode
- `POST /api/v1/auth/register`: optional local USER registration
- `GET /api/v1/auth/me`: authenticated subject, issuer and roles
- `GET /api/v1/admin/health`: administrator role required
- `/docs`: OpenAPI UI with the standard Bearer authorization scheme; paste an access token

`BACKEND_CORS_ORIGINS` is a JSON array of explicit browser origins; the default permits none. Configure the actual frontend origins. CORS does not replace authentication.

## Database and migrations

`RootContainer.db` owns one engine/session factory per process. Inject it into domain containers; domains do not create their own engines or database credentials. Models share `Base.metadata`, native PostgreSQL UUID/JSONB types and timezone-aware timestamps. The example model is included in the initial migration as a working schema reference; its router remains unregistered until you choose to expose the example feature.

Alembic is the only schema history. Import every persisted model in `src/models.py` so autogeneration sees it.

```sh
alembic revision --autogenerate -m "Add products"
# Review the generated migration before applying it.
alembic upgrade head
alembic check
alembic current
```

Run migrations once per deployment before starting/scaling API workers, never independently in every worker. `alembic downgrade -1` reverses the initial migration by dropping the example table; use downgrades only against disposable environments or after reviewing data-loss implications. Production requires tested backups and a deployment-specific recovery plan.

**Already using the PostgreSQL/OIDC revision?** Run `alembic upgrade head` to add the local user table without resetting the existing database. Set `AUTH_MODE=local`, generate a signing secret, and create accounts through the management command.

**Upgrading an older MySQL installation:** this is a breaking baseline for a fresh PostgreSQL database. It does not convert previous MySQL/per-service databases, passwords or admin records. Back up existing data, migrate domain data separately with explicit UUID/timezone conversion, and recreate local accounts with the management command (or provision identities at your optional provider). Associate future user-owned records with the verified `(issuer, subject)` pair, not usernames or email. Do not stamp an existing schema at `head` without reconciling it against the migration. Old SQL files and custom authentication headers have been removed.

## Adding a domain

Copy `src/service_template`, rename its model/service/container/routes, and register persisted models in `src/models.py`. Register the container with `db=db` in `RootContainer`, add its route module to root wiring, then include its router in `create_app`. Reuse `get_current_user` for authenticated routes or `Depends(require_roles("ADMIN", "SUPERADMIN"))` for privileged routes. The copyable template currently uses authenticated access; decide the role policy for writes before exposing it.

The normal flow is routes → services → DAL → shared database. DAL methods own short transactions. Use native `Uuid`, `JSONB` and `DateTime(timezone=True)` consistently. Create and review an Alembic revision for each schema change. No per-service SQL scripts or database lifecycle hooks are needed.

The template limits names to 255 characters. PATCH changes only supplied fields:
`{"meta": null}` clears metadata, while omitted fields remain unchanged. A null
name is rejected. An empty PATCH returns the current record without changing
`updated_at`. Updates and deletes target the UUID atomically and return 404 when
the record no longer exists, including when another request has deleted it.

## Tests

```sh
pytest -q
```

Unit/API tests use generated RSA keys and mocked discovery/JWKS/DAL access. The PostgreSQL integration test is skipped unless `TEST_DATABASE_URL` points to a **dedicated disposable database**:

```sh
TEST_DATABASE_URL=postgresql+asyncpg://fasten:password@localhost:5432/fasten_test pytest -q
```

That test upgrades from the baseline, checks metadata drift, exercises shared-container CRUD, downgrades and re-upgrades. CI runs on Python 3.12 with a real PostgreSQL service. The lock file fixes dependency resolution; update it deliberately with `uv pip compile requirements.txt --python-version 3.12 --universal -o requirements.lock` and rerun the suite.

## Logging

JSON logs include request IDs, feature tags and operation durations. `src.log` provides `get_feature_logger`, `operation_log`, and contextual fields. SQL parameters are hidden in engine errors. Do not log tokens, Authorization headers, credentials or raw request bodies. Settings live in `.env` locally and should come from your deployment secret store in production; `.dockerignore` excludes local environment files from images.
