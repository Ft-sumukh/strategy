from datetime import datetime
from typing import List
from sqlalchemy import Float, ForeignKey, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin, utc_now


class Portfolio(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """User portfolio container.

    A portfolio belongs to a user (via ``user_id``) and aggregates holdings and snapshots.
    """

    __tablename__ = "portfolio"

    name: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[str] = mapped_column(String(256), nullable=True)
    user_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True, default="default_user", doc="FK to auth.user.id")

    holdings: Mapped[List["PortfolioHolding"]] = relationship(
        "PortfolioHolding",
        back_populates="portfolio",
        cascade="all, delete-orphan",
        lazy="selectin",
        uselist=True,
    )
    snapshots: Mapped[List["PortfolioSnapshot"]] = relationship(
        "PortfolioSnapshot",
        back_populates="portfolio",
        cascade="all, delete-orphan",
        lazy="selectin",
        uselist=True,
    )

    __table_args__ = (
        Index("ix_portfolio_user_name", "user_id", "name", unique=True),
    )

    def __repr__(self) -> str:
        return f"<Portfolio(id={self.id}, name={self.name}, user_id={self.user_id})>"

    def total_weight(self) -> float:
        """Return sum of holding weights (in decimal, not percentage)."""
        holdings = self.holdings if isinstance(self.holdings, list) else ([self.holdings] if self.holdings else [])
        return sum(h.weight for h in holdings)

    def validate_weights(self, tolerance: float = 0.001) -> None:
        """Raise ValueError if total weight deviates from 1.0 beyond tolerance."""
        total = self.total_weight()
        if abs(total - 1.0) > tolerance:
            raise ValueError(f"Portfolio weight must sum to 1.0 (got {total:.4f})")


class PortfolioHolding(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Single security holding within a portfolio.

    ``weight`` is expressed as a decimal fraction of the total portfolio (e.g., 0.10 for 10%).
    """

    __tablename__ = "portfolio_holding"

    portfolio_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("portfolio.id", ondelete="CASCADE"), nullable=False, index=True
    )
    ticker: Mapped[str] = mapped_column(String(16), nullable=False)
    weight: Mapped[float] = mapped_column(Float, nullable=False, doc="Decimal fraction of portfolio")
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    cost_basis: Mapped[float] = mapped_column(Float, nullable=False, default=0.0, doc="Avg price per share")
    commission_rate: Mapped[float] = mapped_column(Float, nullable=False, default=0.0, doc="Commission as fraction of trade value")
    slippage_percent: Mapped[float] = mapped_column(Float, nullable=False, default=0.0, doc="Slippage as percent of price")

    portfolio: Mapped[Portfolio] = relationship("Portfolio", back_populates="holdings")

    __table_args__ = (
        Index("ix_holding_portfolio_ticker", "portfolio_id", "ticker", unique=True),
    )

    def __repr__(self) -> str:
        return f"<PortfolioHolding(id={self.id}, ticker={self.ticker}, weight={self.weight})>"


class PortfolioSnapshot(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Snapshot of portfolio performance at a point in time.

    Metrics are stored as decimals (e.g., ``return`` = 0.12 for 12%).
    """

    __tablename__ = "portfolio_snapshot"

    portfolio_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("portfolio.id", ondelete="CASCADE"), nullable=False, index=True
    )
    snapshot_date: Mapped[datetime] = mapped_column(nullable=False, index=True)
    total_value: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    cash: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    return_: Mapped[float] = mapped_column("return", Float, nullable=False, default=0.0)
    volatility: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    sharpe: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    portfolio: Mapped[Portfolio] = relationship("Portfolio", back_populates="snapshots")

    __table_args__ = (
        Index("ix_snapshot_portfolio_date", "portfolio_id", "snapshot_date", unique=True),
    )

    def __repr__(self) -> str:
        return f"<PortfolioSnapshot(id={self.id}, date={self.snapshot_date.date()}, value={self.total_value})>"
