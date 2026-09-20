"""
AEGIS INVEST — SQLAlchemy Declarative Base & Core Mixins
Unifies declarative base across app.db and app.database namespaces.
"""

from app.database.base import (
    Base,
    TimestampMixin,
    UUIDPrimaryKeyMixin,
    utc_now,
    MONETARY_PRECISION,
    MONETARY_SCALE,
    RATE_PRECISION,
    RATE_SCALE,
)

__all__ = [
    "Base",
    "TimestampMixin",
    "UUIDPrimaryKeyMixin",
    "utc_now",
    "MONETARY_PRECISION",
    "MONETARY_SCALE",
    "RATE_PRECISION",
    "RATE_SCALE",
]
