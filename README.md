# FastAPI Backend Template

A production-ready FastAPI boilerplate. Ships with **auth** and **admin** as built-in services and a **`service_template/`** folder you copy-paste to add any new domain (product, order, user, etc.).

---

## Table of contents

1. [Tech stack](#tech-stack)
2. [Project structure](#project-structure)
3. [Quick start](#quick-start)
4. [Configuration](#configuration)
5. [Database setup](#database-setup)
6. [Running the server](#running-the-server)
7. [API overview](#api-overview)
8. [Logging](#logging)
9. [Adding a new service](#adding-a-new-service)
10. [Testing](#testing)
11. [Docker](#docker)

---

## Tech stack

| Layer | Library |
|---|---|
| Web framework | [FastAPI](https://fastapi.tiangolo.com/) |
| ASGI server | [Uvicorn](https://www.uvicorn.org/) |
| ORM | [SQLAlchemy 2 (async)](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html) |
| DI container | [dependency-injector](https://python-dependency-injector.ets-labs.org/) |
| Settings | [pydantic-settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/) |
| DB driver (default) | [aiomysql](https://aiomysql.readthedocs.io/) — MySQL / MariaDB |

Supported async drivers (swap via `DB_DRIVER` in `.env`):

| Database | Driver | Install |
|---|---|---|
| MySQL / MariaDB | `mysql+aiomysql` | `aiomysql` (default, already in requirements) |
| PostgreSQL | `postgresql+asyncpg` | uncomment `asyncpg` in `requirements.txt` |
| SQLite (dev/test) | `sqlite+aiosqlite` | uncomment `aiosqlite` in `requirements.txt` |

---

## Project structure

```
server/
├── src/
│   ├── main.py               # FastAPI app factory + CORS + lifespan
│   ├── container.py          # Root DI container — wires all service containers
│   ├── config.py             # DBConfig: shared DB settings + db_url() builder
│   ├── async_database.py     # AsyncDatabase wrapper (engine, session factory)
│   ├── db_types.py           # FormattedUUID SQLAlchemy type (CHAR(32), no hyphens)
│   ├── utils.py              # PaginatedResponse, @paginate decorator, utcnow()
│   │
│   ├── log/                  # JSON logging: request correlation, operation spans, feature tags
│   │   ├── config.py         # LoggingConfig (LOG_LEVEL, skip_paths, extra_headers)
│   │   ├── setup.py          # setup_logging() — configures the root logger
│   │   ├── formatter.py      # JsonFormatter
│   │   ├── context.py        # request_id / bind_log_context contextvars
│   │   ├── logger.py         # FeatureLogger, get_feature_logger
│   │   ├── operations.py     # @operation_log, operation_logger
│   │   └── middleware.py     # RequestLoggingMiddleware (pure ASGI)
│   │
│   ├── auth/                 # Built-in: shared-secret + admin credential auth
│   │   ├── config.py         # AuthConfig (CLIENT_SHARED_SECRET, ADMIN_*)
│   │   ├── container.py      # AuthContainer
│   │   ├── dependencies.py   # verify_client_secret / verify_admin_credentials
│   │   ├── dto.py
│   │   ├── errors.py
│   │   ├── routes.py         # POST /auth/admin/login (v2 stub)
│   │   └── service.py        # AuthService
│   │
│   ├── admin/                # Built-in: admin orchestration layer
│   │   ├── container.py      # AdminContainer
│   │   ├── dto.py
│   │   ├── errors.py
│   │   ├── routes.py         # GET /api/v1/admin/health
│   │   └── service.py        # AdminService (delegates to domain services)
│   │
│   └── service_template/     # Copy-paste skeleton for any new service
│       ├── __init__.py
│       ├── config.py
│       ├── container.py
│       ├── dal.py            # Data Access Layer
│       ├── dto.py            # Pydantic DTOs
│       ├── errors.py         # HTTPException subclasses
│       ├── service.py        # Business logic
│       ├── routes.py         # FastAPI router stubs
│       ├── models/
│       │   └── example.py    # SQLAlchemy model template
│       ├── enums/
│       │   └── enum.py
│       └── services/
│           └── example_worker.py  # Sub-service template
│
├── sql/
│   ├── template.00.sql       # DB + user creation template (MySQL + PG variants)
│   └── template.01.sql       # Table creation template (MySQL + PG variants)
│
├── tests/
│   ├── conftest.py           # auth_config, auth_service fixtures
│   ├── auth/
│   │   └── test_service.py
│   ├── admin/
│   │   └── test_service.py
│   └── common/
│       └── test_utils.py
│
├── .env.example
├── .env                      # gitignored — copy from .env.example
├── Dockerfile
├── docker-compose.yml        # MySQL by default; PostgreSQL alternative included
├── requirements.txt
└── pytest.ini
```

---

## Quick start

### Prerequisites

- Python 3.12+
- Docker + Docker Compose (for the database)

### 1. Clone and create the virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure the environment

```bash
cp .env.example .env
```

Edit `.env` — the minimum required values:

```dotenv
DB_DRIVER=mysql+aiomysql     # or postgresql+asyncpg / sqlite+aiosqlite
DB_HOST=0.0.0.0
DB_PORT=3306
DB_DEFAULT_PASSWORD=your_password

CLIENT_SHARED_SECRET=change_me_in_production
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your_password
```

### 3. Start the database

```bash
docker compose up -d
```

This starts MySQL (or PostgreSQL if you switched the service in `docker-compose.yml`) and automatically runs every `sql/*.sql` file to initialise the database.

### 4. Start the API

```bash
uvicorn src.main:app --reload
```

The API is now available at `http://localhost:8000`.  
Interactive docs: `http://localhost:8000/docs`

---

## Configuration

All settings live in `.env` and are loaded by **pydantic-settings**.

| Variable | Default | Description |
|---|---|---|
| `DB_DRIVER` | `mysql+aiomysql` | SQLAlchemy async driver string |
| `DB_HOST` | `0.0.0.0` | Database host |
| `DB_PORT` | `3306` | Database port |
| `DB_DEFAULT_PASSWORD` | `test1234` | Default DB user password (override per service if needed) |
| `DB_ECHO` | `false` | Log every SQL statement (dev only) |
| `DB_CONN_ECHO` | `false` | Log connection pool events |
| `LOG_LEVEL` | `INFO` | Root logger level for the JSON stdout logs |
| `CLIENT_SHARED_SECRET` | — | Secret the frontend sends in `X-Client-Secret` header |
| `ADMIN_USERNAME` | `admin` | Admin username for `X-Admin-Username` header |
| `ADMIN_PASSWORD` | — | Admin password for `X-Admin-Password` header |

### Database URLs

`DBConfig.db_url(service_name)` builds the connection URL automatically:

```
<DB_DRIVER>://<service_name>_user:<DB_DEFAULT_PASSWORD>@<DB_HOST>:<DB_PORT>/<service_name>_db
```

Example — a `product` service with `DB_DRIVER=postgresql+asyncpg`:
```
postgresql+asyncpg://product_user:your_password@0.0.0.0:5432/product_db
```

---

## Database setup

The `sql/` directory contains ordered SQL scripts. Docker Compose mounts the entire directory into the DB container's init folder, so all scripts run on first startup (alphabetical order).

**File naming convention:** `<service_name>.<order>.sql`

| File | Purpose |
|---|---|
| `template.00.sql` | Create database + user (template — copy and rename) |
| `template.01.sql` | Create tables (template — copy and rename) |

When you add a new service, copy the templates:

```bash
cp sql/template.00.sql sql/product.00.sql
cp sql/template.01.sql sql/product.01.sql
# Then edit both files, replacing <service_name> with "product"
```

> **Resetting the database:** stop the containers, delete the `.data/` directory, then restart.
> ```bash
> docker compose down
> rm -rf .data/
> docker compose up -d
> ```

---

## Running the server

**Development (with auto-reload):**
```bash
uvicorn src.main:app --reload
```

**Production:**
```bash
uvicorn src.main:app --host 0.0.0.0 --port 8000 --workers 4
```

---

## API overview

### Authentication

All user-facing routes require the `X-Client-Secret` header to match the `CLIENT_SHARED_SECRET` env variable. This is validated by the `verify_client_secret` FastAPI dependency.

Admin routes (v2) will use `X-Admin-Username` / `X-Admin-Password` headers via `verify_admin_credentials`.

### Built-in endpoints

| Method | Path | Auth | Description |
|---|---|---|---|
| `GET` | `/health` | None | Liveness check |
| `POST` | `/auth/admin/login` | None | Admin login stub (v2) |
| `GET` | `/api/v1/admin/health` | None | Admin service health |

### Response format for paginated lists

All paginated endpoints return:

```json
{
  "items": [...],
  "total": 42,
  "page": 1,
  "size": 10
}
```

---

## Logging

`src/log/` provides JSON-on-stdout logging, wired in automatically by `create_app()` (`setup_logging()` + `RequestLoggingMiddleware`, `src/main.py`). One JSON object per line — ready for CloudWatch, Datadog, Loki, or GCP Logging.

Every request gets an `X-Request-ID` (echoed from the incoming header, or generated) that's attached to every log line for that request, plus an `X-Process-Time` response header. `/health`, `/docs`, `/redoc`, `/openapi.json` don't emit request start/complete lines (see `LoggingConfig.skip_paths`).

**In a service module:**

```python
from src.log import get_feature_logger, operation_log

logger = get_feature_logger(__name__, feature="auth")  # feature = bounded-context name


class AuthService:
    @operation_log("verify_client_secret", feature="auth")
    def verify_client_secret(self, secret: str) -> bool:
        ...
```

- `get_feature_logger(__name__, feature=...)` — one per service module; tags every line with `feature` so logs can be filtered per bounded context (`auth`, `admin`, `service_template`, ...).
- `@operation_log("verb_noun", feature=...)` — put on public service methods. Logs start / complete (+ `duration_ms`) / failed (+ `error`, `error_type`, `exc_info`), sync and async both supported. Use `operation_logger(...)` as a context manager for non-method blocks (worker jobs, scripts).
- `bind_log_context(**kwargs)` — attach extra fields (e.g. `user_id`) to every log line for the rest of the request/task; call it from an auth dependency or worker entrypoint.

**Do not log** passwords, tokens, raw request/response bodies, or unmasked PII — IDs and metadata only. Use `logger.error(...)`, never `print()`.

Workers/CLI entrypoints that share app code should call `setup_logging()` once at start and use the same loggers/decorator (no HTTP middleware needed outside a request).

Tests live in `tests/log/`, mirroring `src/log/`.

---

## Adding a new service

Follow these five steps to wire up a new domain (example: `product`).

### Step 1 — Copy the service template

```bash
cp -r src/service_template src/product
```

### Step 2 — Rename everything

Inside `src/product/`, replace all `service_template` / `ServiceTemplate` / `example` / `Example` occurrences with your domain name. Files to update:

- `config.py` — rename `ServiceConfig` → `ProductConfig`, `get_service_config` → `get_product_config`
- `container.py` — rename `ServiceContainer` → `ProductContainer`; update `db_url("service_template")` → `db_url("product")`; update the wiring module path
- `dal.py` — rename `ServiceDal` → `ProductDal`; update model imports
- `service.py` — rename `ServiceLayer` → `ProductService`; update imports
- `routes.py` — rename tag, update `Provide["service_template.service"]` → `Provide["product.service"]`
- `models/example.py` — rename `ExampleModel` to your entity; update `__tablename__`
- `dto.py` — rename DTOs to match your entity
- `errors.py` — rename error classes
- `enums/enum.py` — replace `ExampleStatus` with relevant enums
- `service.py` — update the `feature="service_template"` values (logger + `@operation_log` calls) to your new service's name, see [Logging](#logging)

### Step 3 — Create the SQL scripts

```bash
cp sql/template.00.sql sql/product.00.sql
cp sql/template.01.sql sql/product.01.sql
```

Edit both files: replace `<service_name>` with `product`.

### Step 4 — Register the container in `src/container.py`

```python
from src.product.container import ProductContainer

class RootContainer(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        modules=[
            "src.auth.dependencies",
            "src.admin.routes",
            "src.product.routes",       # add this
        ]
    )

    db_config = providers.Singleton(get_db_config)
    auth = providers.Container(AuthContainer)
    admin = providers.Container(AdminContainer)

    product = providers.Container(               # add this
        ProductContainer,
        db_config=db_config,
    )
```

### Step 5 — Register the router in `src/main.py`

```python
from src.product.routes import router as product_router

app.include_router(product_router)
```

And connect the DB in the lifespan:

```python
async def lifespan(app):
    await container.product.db().connect()
    yield
    await container.product.db().disconnect()
```

### Step 6 — Reset and restart

```bash
docker compose down && rm -rf .data/ && docker compose up -d
uvicorn src.main:app --reload
```

---

## Testing

Tests use **pytest** + **pytest-asyncio** (all tests run in `auto` asyncio mode).

```bash
# Install dependencies (if not already done)
pip install -r requirements.txt

# Run all tests
pytest

# Run with verbose output
pytest -v

# Run a specific module
pytest tests/auth/
```

The test suite covers:
- `tests/auth/` — `AuthService` (shared-secret + admin credential validation)
- `tests/admin/` — `AdminService`
- `tests/common/` — `PaginatedResponse`, `@paginate` decorator, `utcnow()`
- `tests/log/` — JSON formatter, request-id/context propagation, feature logger, `@operation_log`, `RequestLoggingMiddleware`

Domain-specific tests go in `tests/<service_name>/`. Use `AsyncMock` from the standard library to stub the DAL — no database connection required.

---

## Docker

### Development (database only)

```bash
docker compose up -d        # start DB
docker compose down         # stop DB
docker compose logs -f db   # stream logs
```

### Full stack (API + database)

```bash
docker compose up --build
```

The `Dockerfile` builds the API image using Python 3.12-slim and runs `uvicorn` on port `8000`.

### Switching to PostgreSQL

1. In `docker-compose.yml`, comment out the MySQL `db` service and uncomment the PostgreSQL block.
2. In `.env`, set `DB_DRIVER=postgresql+asyncpg`.
3. In `requirements.txt`, comment out `aiomysql` and uncomment `asyncpg`.
4. Update your `sql/*.sql` scripts to use PostgreSQL syntax (the templates include commented-out PG equivalents).
5. Reset the database: `docker compose down && rm -rf .data/ && docker compose up -d`.
