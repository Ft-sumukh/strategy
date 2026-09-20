"""
AEGIS INVEST — Main Application Entrypoint & Factory
Bootstraps FastAPI, configures lifecycle management, registers middlewares,
exception handlers, and mounts versioned API routes.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.api.v1.router import api_v1_router
from app.core.config import get_settings
from app.core.errors import register_exception_handlers
from app.core.logging import get_logger, setup_logging
from app.core.security import SecurityHeadersMiddleware, configure_cors
from app.db.base import Base
from app.db.session import check_db_connectivity, engine
from app.middleware.logging_middleware import LoggingMiddleware
from app.middleware.metrics import MetricsMiddleware
from app.middleware.request_id import RequestIDMiddleware

settings = get_settings()
setup_logging(log_level=settings.log_level, log_format=settings.log_format)
logger = get_logger("aegis.main")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifecycle management (startup and shutdown events)."""
    logger.info(
        f"Starting {settings.app_name} v{settings.app_version} in [{settings.app_env}] mode"
    )

    # Initialize tables if SQLite (for local/testing zero-config runs)
    if settings.database_url.startswith("sqlite"):
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("SQLite local database schemas initialized")

    # Verify database connectivity
    db_alive = await check_db_connectivity()
    if db_alive:
        logger.info("Database connectivity established successfully")
    else:
        logger.warning("Database connection is not currently responding")

    yield

    # Clean shutdown
    logger.info(f"Shutting down {settings.app_name}...")
    await engine.dispose()
    logger.info("Database connection pool disposed cleanly")


def create_application() -> FastAPI:
    """Factory creating and configuring the FastAPI application instance."""
    app = FastAPI(
        title="AEGIS INVEST API",
        description=(
            "Production-oriented financial investment decision-intelligence API foundation. "
            "Engineered for high reliability, strict data integrity, and modular quant research."
        ),
        version=settings.app_version,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # 1. Register Middlewares (order matters: executed outer-to-inner)
    app.add_middleware(MetricsMiddleware)
    app.add_middleware(LoggingMiddleware)
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(RequestIDMiddleware)
    configure_cors(app, settings.parsed_cors_origins)

    # 2. Register Exception Handlers
    register_exception_handlers(app, is_production=settings.is_production)

    # 3. Mount Versioned API Routers
    app.include_router(api_v1_router, prefix=settings.api_v1_prefix)

    # 4. Root Route
    @app.get("/", tags=["Root"], include_in_schema=False)
    async def root_redirect() -> JSONResponse:
        return JSONResponse({
            "service": settings.app_name,
            "version": settings.app_version,
            "environment": settings.app_env,
            "docs": "/docs",
            "api_v1": settings.api_v1_prefix,
        })

    return app


app = create_application()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
    )
