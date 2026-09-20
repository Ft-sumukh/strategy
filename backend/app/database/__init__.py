"""
AEGIS INVEST — Database Foundation
Provides SQLAlchemy declarative base, session factory, and database connection lifecycle.
"""

from app.database.base import (
    Base,
    TimestampMixin,
    UUIDPrimaryKeyMixin,
    MONETARY_PRECISION,
    MONETARY_SCALE,
    RATE_PRECISION,
    RATE_SCALE,
    utc_now,
)
from app.database.session import (
    AsyncSessionLocal,
    check_db_connectivity,
    create_engine_for_url,
    engine,
    get_db,
)

__all__ = [
    "Base",
    "TimestampMixin",
    "UUIDPrimaryKeyMixin",
    "MONETARY_PRECISION",
    "MONETARY_SCALE",
    "RATE_PRECISION",
    "RATE_SCALE",
    "utc_now",
    "AsyncSessionLocal",
    "check_db_connectivity",
    "create_engine_for_url",
    "engine",
    "get_db",
]
