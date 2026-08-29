from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.container import RootContainer
from src.log import RequestLoggingMiddleware, get_logging_config, setup_logging


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    container: RootContainer = app.container  # type: ignore[attr-defined]
    # TODO: connect each service DB here, e.g.:
    # await container.my_service.db().connect()
    yield
    # TODO: disconnect each service DB here, e.g.:
    # await container.my_service.db().disconnect()


def create_app() -> FastAPI:
    logging_config = get_logging_config()
    setup_logging(level=logging_config.LOG_LEVEL)

    container = RootContainer()

    app = FastAPI(
        title="API Template",
        description="FastAPI boilerplate with auth, admin, and pluggable services.",
        version="0.1.0",
        lifespan=lifespan,
    )

    app.container = container  # type: ignore[attr-defined]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    # Registered after CORS so it wraps the stack as the outermost
    # middleware (Starlette runs the most-recently-added middleware first).
    app.add_middleware(RequestLoggingMiddleware, settings=logging_config)

    from src.auth.routes import router as auth_router
    from src.admin.routes import router as admin_router
    # TODO: import and register your service routers here, e.g.:
    # from src.my_service.routes import router as my_service_router

    app.include_router(auth_router)
    app.include_router(admin_router, prefix="/api/v1")
    # TODO: app.include_router(my_service_router)

    @app.get("/health", tags=["health"])
    async def health_check() -> dict:
        return {"status": "ok"}

    return app


app = create_app()
