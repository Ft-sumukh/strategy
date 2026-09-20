"""
AEGIS INVEST — Market Regime Domain Models
Defines persistent entities for market regime classifications and historical timeline tracking.
"""

from datetime import datetime
from sqlalchemy import DateTime, Float, Index, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class MarketRegimeRecord(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    Market regime assessment snapshot.
    Classifies macro/market states into deterministic regimes:
    BULL_TREND, BEAR_TREND, SIDEWAYS, HIGH_VOLATILITY, LOW_VOLATILITY, RISK_ON, RISK_OFF, TRANSITION.
    """
    __tablename__ = "market_regimes"

    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    regime: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    confidence: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    previous_regime: Mapped[str] = mapped_column(String(50), nullable=True)
    duration_days: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    supporting_signals: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    methodology: Mapped[str] = mapped_column(Text, nullable=False)
    data_source: Mapped[str] = mapped_column(String(50), nullable=False, default="aegis_regime_engine")

    __table_args__ = (
        Index("ix_regime_timestamp_desc", timestamp.desc()),
    )
