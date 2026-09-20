"""
AEGIS INVEST — Foundation Models
Establishes the minimal required persistent infrastructure models
(SystemAudit) to verify migrations, session management, and database operations.
"""

from datetime import datetime
from sqlalchemy import DateTime, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin, utc_now


class SystemAudit(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    System Audit Model.
    Records system bootstrap events, readiness evaluations, and component status transitions.
    """

    __tablename__ = "system_audit"

    event_type: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        index=True,
        doc="Type of system event: BOOTSTRAP, HEALTH_CHECK, MIGRATION, CONFIG_CHANGE",
    )
    component: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        index=True,
        doc="Subsystem or service name emitting the event",
    )
    status: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default="OK",
        doc="Status code: OK, WARNING, ERROR, DEGRADED",
    )
    message: Mapped[str] = mapped_column(
        Text,
        nullable=True,
        default=None,
        doc="Descriptive context or details regarding the event",
    )
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
        index=True,
        doc="Timestamp when the event occurred in UTC",
    )

    __table_args__ = (
        Index("idx_system_audit_event_recorded", "event_type", "recorded_at"),
    )

    def __repr__(self) -> str:
        return f"<SystemAudit(id={self.id}, event_type='{self.event_type}', component='{self.component}', status='{self.status}')>"
