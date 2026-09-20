"""
AEGIS INVEST — Systematic Strategy Domain Models
Defines persistent entities for Strategy Definitions and reproducible Strategy Signals.
"""

from datetime import datetime
from sqlalchemy import Boolean, DateTime, Float, Index, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class StrategyDefinition(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Declarative specification for a systematic quantitative alpha model or asset allocation strategy."""
    __tablename__ = "strategy_definitions"

    strategy_key: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, index=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False, default="FACTOR")  # FACTOR, TECHNICAL, ALLOCATION
    description: Mapped[str] = mapped_column(Text, nullable=False)
    universe: Mapped[str] = mapped_column(String(100), nullable=False, default="US_LARGE_CAP")
    rebalance_frequency: Mapped[str] = mapped_column(String(30), nullable=False, default="monthly")

    parameters: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    risk_constraints: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)

    version: Mapped[str] = mapped_column(String(20), nullable=False, default="1.0")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


class StrategySignalRecord(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Reproducible point-in-time signal and portfolio weight emitted by a systematic strategy."""
    __tablename__ = "strategy_signals"

    strategy_key: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    ticker: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    signal_score: Mapped[float] = mapped_column(Float, nullable=False)  # Normalized signal score
    rank: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    target_weight: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)  # Decimal target weight (0.0 - 1.0)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    strategy_version: Mapped[str] = mapped_column(String(20), nullable=False, default="1.0")
    rationale: Mapped[str] = mapped_column(Text, nullable=True)

    __table_args__ = (
        Index("ix_strat_signal_lookup", "strategy_key", "ticker", "timestamp"),
    )
