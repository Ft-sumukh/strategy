"""
AEGIS INVEST — Risk & Stress Testing Domain Models
Defines persistent entities for portfolio risk decomposition, factor sensitivities,
and historical/hypothetical stress scenarios.
"""

from datetime import datetime
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Index, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin, utc_now


class RiskMetricRecord(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Calculated risk breakdown for a portfolio or asset universe."""
    __tablename__ = "risk_metric_records"

    entity_type: Mapped[str] = mapped_column(String(30), nullable=False, default="PORTFOLIO")  # PORTFOLIO, ASSET, BENCHMARK
    entity_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    as_of_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)

    annualized_volatility: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    downside_deviation: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    var_95: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)  # Value at Risk 95%
    var_99: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)  # Value at Risk 99%
    cvar_95: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)  # Conditional VaR / Expected Shortfall
    max_drawdown: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    beta: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    hhi_concentration: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)  # Herfindahl-Hirschman Index
    factor_exposures: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)  # Size, Value, Momentum, Quality, Volatility
    sector_exposures: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    correlation_matrix: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)


class StressTestScenario(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Historical or hypothetical market shock scenario definition."""
    __tablename__ = "stress_test_scenarios"

    scenario_key: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, index=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False, default="HISTORICAL")  # HISTORICAL, HYPOTHETICAL, REGIME
    description: Mapped[str] = mapped_column(Text, nullable=False)
    equity_market_shock: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)  # Decimal shock (e.g. -0.20 for -20%)
    rate_shock_bps: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)  # In bps (+100 bps = +1.0%)
    inflation_shock: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    oil_shock: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    vix_spike: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    asset_shocks: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)  # Custom asset-specific shocks
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


class StressTestResult(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Scenario simulation outcome for a specific portfolio."""
    __tablename__ = "stress_test_results"

    portfolio_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    scenario_key: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    estimated_return: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    estimated_drawdown: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    estimated_volatility_spike: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    position_impacts: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    sector_impacts: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    factor_impacts: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    recovery_estimate_months: Mapped[float] = mapped_column(Float, nullable=False, default=6.0)
    rationale: Mapped[str] = mapped_column(Text, nullable=True)
