"""
AEGIS INVEST — Database Engine & Session Lifecycle
Manages asynchronous database connections, session lifecycle,
and connectivity health checks.
"""

from collections.abc import AsyncGenerator
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool

from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger("aegis.db")


def create_engine_for_url(db_url: str, echo: bool = False) -> AsyncEngine:
    """Creates an AsyncEngine with appropriate pooling configurations."""
    is_sqlite = db_url.startswith("sqlite")

    engine_kwargs = {
        "echo": echo,
        "future": True,
    }

    if is_sqlite:
        # SQLite-specific connection parameters for local/test concurrency
        engine_kwargs["connect_args"] = {"check_same_thread": False}
        engine_kwargs["poolclass"] = NullPool
    else:
        # Production PostgreSQL pool settings
        settings = get_settings()
        engine_kwargs["pool_size"] = settings.database_pool_size
        engine_kwargs["max_overflow"] = settings.database_max_overflow
        engine_kwargs["pool_timeout"] = settings.database_pool_timeout
        engine_kwargs["pool_pre_ping"] = True

    return create_async_engine(db_url, **engine_kwargs)


settings = get_settings()
engine: AsyncEngine = create_engine_for_url(settings.database_url, echo=settings.database_echo)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency that yields a managed AsyncSession.
    Automatically rolls back uncommitted transactions on exception and closes the session.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def check_db_connectivity() -> bool:
    """
    Executes a lightweight query (SELECT 1) to verify database health.
    Returns True if reachable, False otherwise.
    """
    try:
        async with AsyncSessionLocal() as session:
            result = await session.execute(text("SELECT 1"))
            return result.scalar() == 1
    except Exception as exc:
        logger.error(f"Database connectivity check failed: {exc}")
        return False
