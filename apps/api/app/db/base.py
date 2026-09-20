"""
AEGIS INVEST — SQLAlchemy Declarative Base & Core Mixins
Defines common table configurations, UTC timestamps, and serialization conventions.
"""

from datetime import datetime, timezone
import uuid
from sqlalchemy import DateTime, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


def utc_now() -> datetime:
    """Returns current timezone-aware UTC datetime."""
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    """Base declarative class for all AEGIS database models."""
    pass


class TimestampMixin:
    """
    Mixin providing created_at and updated_at UTC timestamps.
    Enforces auditability across all persistent entities.
    """

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    )


class UUIDPrimaryKeyMixin:
    """
    Mixin providing a UUID primary key string.
    Ensures distributed uniqueness and prevents sequential enumeration attacks.
    """

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        index=True,
    )
