"""
AEGIS INVEST — Models Base Package
Re-exports Base and common mixins for clean import paths.
"""

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin, utc_now

__all__ = ["Base", "TimestampMixin", "UUIDPrimaryKeyMixin", "utc_now"]
