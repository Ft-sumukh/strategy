"""
AEGIS INVEST — Experiment Lab Domain Models
Defines persistent entities for reproducible quantitative research experiments.
"""

from datetime import datetime
from sqlalchemy import DateTime, Float, Index, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class ExperimentRecord(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    Reproducible quantitative research experiment tracking.
    Enforces immutability of dataset version, strategy version, and execution parameters.
    """
    __tablename__ = "experiment_records"

    name: Mapped[str] = mapped_column(String(200), nullable=False)
    hypothesis: Mapped[str] = mapped_column(Text, nullable=False)
    strategy_key: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    universe: Mapped[str] = mapped_column(String(100), nullable=False, default="US_LARGE_CAP")
    parameters: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)

    date_range: Mapped[str] = mapped_column(String(100), nullable=False, default="2021-01-01_to_2025-12-31")
    rebalance_frequency: Mapped[str] = mapped_column(String(30), nullable=False, default="monthly")
    transaction_cost_bps: Mapped[float] = mapped_column(Float, nullable=False, default=5.0)
    slippage_bps: Mapped[float] = mapped_column(Float, nullable=False, default=2.0)

    dataset_version: Mapped[str] = mapped_column(String(30), nullable=False, default="v1.0-audited")
    strategy_version: Mapped[str] = mapped_column(String(30), nullable=False, default="1.0")
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="COMPLETED")  # COMPLETED, RUNNING, FAILED

    results: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)

    __table_args__ = (
        Index("ix_experiment_strategy_created", "strategy_key", "created_at"),
    )
