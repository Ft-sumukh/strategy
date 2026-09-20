"""
AEGIS INVEST — Macroeconomic Domain Models
Defines persistent entities for Sovereign Macro Series metadata
and point-in-time Macro Observations.
"""

from datetime import datetime
from sqlalchemy import DateTime, Float, ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class MacroSeries(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Metadata catalog for macroeconomic indicators (Fed Funds, CPI, GDP, Yields, VIX)."""
    __tablename__ = "macro_series"

    series_code: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    country: Mapped[str] = mapped_column(String(50), nullable=False, default="USA")
    frequency: Mapped[str] = mapped_column(String(20), nullable=False, default="monthly")  # daily, monthly, quarterly
    unit: Mapped[str] = mapped_column(String(50), nullable=False, default="%")  # %, Index, USD, Bps
    currency: Mapped[str] = mapped_column(String(10), nullable=False, default="USD")
    description: Mapped[str] = mapped_column(Text, nullable=True)
    source: Mapped[str] = mapped_column(String(100), nullable=False, default="FRED_DEMO")

    observations: Mapped[list["MacroObservation"]] = relationship(
        "MacroObservation", back_populates="series", cascade="all, delete-orphan", lazy="selectin"
    )


class MacroObservation(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Individual historical or current observation for a macro series."""
    __tablename__ = "macro_observations"

    series_code: Mapped[str] = mapped_column(
        String(50), ForeignKey("macro_series.series_code", ondelete="CASCADE"), nullable=False, index=True
    )
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    value: Mapped[float] = mapped_column(Float, nullable=False)

    source: Mapped[str] = mapped_column(String(100), nullable=False, default="FRED_DEMO")
    data_version: Mapped[str] = mapped_column(String(20), nullable=False, default="1.0")
    quality_status: Mapped[str] = mapped_column(String(30), nullable=False, default="AUDITED")

    series: Mapped["MacroSeries"] = relationship("MacroSeries", back_populates="observations")

    __table_args__ = (
        Index("ix_macro_obs_code_timestamp", "series_code", "timestamp", unique=True),
    )
