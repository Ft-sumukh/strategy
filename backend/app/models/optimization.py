"""
AEGIS INVEST — Portfolio Optimization Domain Models
Defines persistent entities for mathematical portfolio optimization runs,
target allocations, and efficient frontier points.
"""

from datetime import datetime
from sqlalchemy import DateTime, Float, ForeignKey, Index, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin, utc_now


class OptimizationRunRecord(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Reproducible record of a portfolio optimization solver execution."""
    __tablename__ = "optimization_runs"

    portfolio_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    objective: Mapped[str] = mapped_column(String(50), nullable=False, default="MAX_SHARPE")  # MIN_VARIANCE, MAX_SHARPE, RISK_PARITY, MAX_DIVERSIFICATION, CVAR_AWARE
    universe: Mapped[str] = mapped_column(String(256), nullable=False)
    constraints: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)  # min_weight, max_weight, max_sector_weight, max_turnover
    initial_weights: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    optimized_weights: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    weight_deltas: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)

    expected_return: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    expected_volatility: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    expected_sharpe: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    diversification_ratio: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    solver_status: Mapped[str] = mapped_column(String(30), nullable=False, default="OPTIMAL")  # OPTIMAL, SUBOPTIMAL, FAILED
    iterations: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    notes: Mapped[str] = mapped_column(Text, nullable=True)
