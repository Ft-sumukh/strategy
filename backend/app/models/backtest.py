"""
AEGIS INVEST — Backtesting Domain Models
Defines persistent entities for deterministic backtest configurations, simulation runs,
equity curves, and trade execution logs.
"""

from datetime import datetime
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Index, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin, utc_now


class BacktestConfig(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Configuration blueprint for a deterministic systematic backtest."""
    __tablename__ = "backtest_configs"

    name: Mapped[str] = mapped_column(String(128), nullable=False)
    strategy_key: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    universe: Mapped[str] = mapped_column(String(256), nullable=False, default="AAPL,MSFT,NVDA,GOOG,AMZN")
    start_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    initial_capital: Mapped[float] = mapped_column(Float, nullable=False, default=100000.0)
    rebalance_frequency: Mapped[str] = mapped_column(String(30), nullable=False, default="MONTHLY")
    transaction_cost_bps: Mapped[float] = mapped_column(Float, nullable=False, default=10.0)  # Basis points
    slippage_bps: Mapped[float] = mapped_column(Float, nullable=False, default=5.0)  # Basis points
    max_position_weight: Mapped[float] = mapped_column(Float, nullable=False, default=0.35)
    benchmark: Mapped[str] = mapped_column(String(20), nullable=False, default="SPY")
    parameters: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    user_id: Mapped[str] = mapped_column(String(36), nullable=False, default="default_user", index=True)

    runs: Mapped[list["BacktestRun"]] = relationship(
        "BacktestRun", back_populates="config", cascade="all, delete-orphan", lazy="selectin"
    )


class BacktestRun(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Completed execution result of a backtest with summary metrics."""
    __tablename__ = "backtest_runs"

    config_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("backtest_configs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="COMPLETED")  # PENDING, RUNNING, COMPLETED, FAILED
    total_return: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    cagr: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    annualized_volatility: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    sharpe_ratio: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    sortino_ratio: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    max_drawdown: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    calmar_ratio: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    win_rate: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    turnover: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    trades_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    benchmark_return: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    alpha: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    beta: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    execution_time_ms: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    error_message: Mapped[str] = mapped_column(Text, nullable=True)

    config: Mapped[BacktestConfig] = relationship("BacktestConfig", back_populates="runs")
    equity_points: Mapped[list["BacktestEquityPoint"]] = relationship(
        "BacktestEquityPoint", back_populates="run", cascade="all, delete-orphan", lazy="selectin"
    )
    trades: Mapped[list["BacktestTrade"]] = relationship(
        "BacktestTrade", back_populates="run", cascade="all, delete-orphan", lazy="selectin"
    )


class BacktestEquityPoint(Base, UUIDPrimaryKeyMixin):
    """Daily equity curve point for a backtest run."""
    __tablename__ = "backtest_equity_points"

    run_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("backtest_runs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    equity: Mapped[float] = mapped_column(Float, nullable=False)
    drawdown: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    benchmark_equity: Mapped[float] = mapped_column(Float, nullable=False, default=100000.0)

    run: Mapped[BacktestRun] = relationship("BacktestRun", back_populates="equity_points")

    __table_args__ = (
        Index("ix_equity_run_date", "run_id", "date", unique=True),
    )


class BacktestTrade(Base, UUIDPrimaryKeyMixin):
    """Individual rebalance transaction record."""
    __tablename__ = "backtest_trades"

    run_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("backtest_runs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    ticker: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    side: Mapped[str] = mapped_column(String(10), nullable=False)  # BUY, SELL
    shares: Mapped[float] = mapped_column(Float, nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    transaction_cost: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    slippage: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    target_weight: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    run: Mapped[BacktestRun] = relationship("BacktestRun", back_populates="trades")
