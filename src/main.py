from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from src.config import get_settings
from src.container import RootContainer
from src.log import RequestLoggingMiddleware, get_logging_config, setup_logging


@asynccontextmanager
async def lifespan(app: FastAPI):
    container = app.container
    # Fail closed on missing OIDC configuration, without making provider network calls.
    container.auth.config()
    db = container.db()
    try:
        await db.check()
        yield
    finally:
        await db.disconnect()


def create_app() -> FastAPI:
    settings = get_settings()
    logging = get_logging_config()
    setup_logging(level=logging.LOG_LEVEL)
    container = RootContainer()
    app = FastAPI(title=settings.PROJECT_NAME, version="0.2.0", lifespan=lifespan)
    app.container = container
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PATCH", "DELETE"],
        allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
    )
    app.add_middleware(RequestLoggingMiddleware, settings=logging)
    from src.admin.routes import router as admin_router
    from src.auth.routes import router as auth_router

    app.include_router(auth_router, prefix=settings.API_V1_STR)
    app.include_router(admin_router, prefix=settings.API_V1_STR)

    @app.get("/health", tags=["health"])
    async def health():
        return {"status": "ok"}

    @app.get("/ready", tags=["health"])
    async def ready():
        try:
            await container.db().check()
        except Exception:
            raise HTTPException(503, "Database unavailable") from None
        return {"status": "ok"}

    @app.get("/", tags=["meta"])
    async def root():
        return {"name": app.title, "version": app.version, "docs": "/docs"}

    return app


app = create_app()
