"""
AEGIS INVEST — Financial Intelligence Domain Models
Defines persistent entities for Companies, Market Price Bars, and Normalized Financial Statements
(Income Statement, Balance Sheet, Cash Flow Statement).
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Numeric,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import (
    Base,
    MONETARY_PRECISION,
    MONETARY_SCALE,
    RATE_PRECISION,
    RATE_SCALE,
    TimestampMixin,
    UUIDPrimaryKeyMixin,
    utc_now,
)


class Company(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    Company Master Entity.
    Stores institutional master metadata, classification, and capitalization metrics.
    """

    __tablename__ = "companies"

    ticker: Mapped[str] = mapped_column(
        String(16),
        unique=True,
        nullable=False,
        index=True,
        doc="Primary trading ticker symbol (e.g. AAPL, NVDA)",
    )
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
        doc="Full legal entity / corporate name",
    )
    exchange: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        doc="Primary listing exchange (e.g. NASDAQ, NYSE)",
    )
    sector: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        index=True,
        doc="GICS Sector classification",
    )
    industry: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
        index=True,
        doc="GICS Industry classification",
    )
    country: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        default="United States",
        doc="Country of domicile / incorporation",
    )
    currency: Mapped[str] = mapped_column(
        String(8),
        nullable=False,
        default="USD",
        doc="Functional reporting currency",
    )
    description: Mapped[str] = mapped_column(
        Text,
        nullable=True,
        doc="Comprehensive business description and operating model",
    )
    website: Mapped[str] = mapped_column(
        String(255),
        nullable=True,
        doc="Corporate investor relations website",
    )
    market_cap: Mapped[Decimal] = mapped_column(
        Numeric(MONETARY_PRECISION, MONETARY_SCALE),
        nullable=True,
        doc="Market capitalization in functional currency",
    )
    shares_outstanding: Mapped[Decimal] = mapped_column(
        Numeric(MONETARY_PRECISION, MONETARY_SCALE),
        nullable=True,
        doc="Total common shares outstanding",
    )
    status: Mapped[str] = mapped_column(
        String(16),
        nullable=False,
        default="ACTIVE",
        doc="Listing status: ACTIVE, DELISTED, SUSPENDED",
    )
    is_synthetic: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        doc="True if seeded from demo dataset; False for verified real data",
    )

    # Relationships
    price_bars = relationship(
        "MarketPriceBar",
        back_populates="company",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    income_statements = relationship(
        "IncomeStatement",
        back_populates="company",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    balance_sheets = relationship(
        "BalanceSheet",
        back_populates="company",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    cash_flow_statements = relationship(
        "CashFlowStatement",
        back_populates="company",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Company(ticker='{self.ticker}', name='{self.name}', sector='{self.sector}')>"


class MarketPriceBar(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    Market Price Bar (OHLCV) Entity.
    Stores historical daily and intraday price series with split/dividend adjustment lineage.
    """

    __tablename__ = "market_price_bars"

    ticker: Mapped[str] = mapped_column(
        String(16),
        ForeignKey("companies.ticker", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
        doc="Bar open timestamp in UTC",
    )
    open: Mapped[float] = mapped_column(Float, nullable=False)
    high: Mapped[float] = mapped_column(Float, nullable=False)
    low: Mapped[float] = mapped_column(Float, nullable=False)
    close: Mapped[float] = mapped_column(Float, nullable=False)
    adj_close: Mapped[float] = mapped_column(Float, nullable=False)
    volume: Mapped[float] = mapped_column(Float, nullable=False)
    vwap: Mapped[float] = mapped_column(Float, nullable=True)
    interval: Mapped[str] = mapped_column(
        String(16),
        nullable=False,
        default="1d",
        doc="Bar frequency: 1d, 1h, 15m, etc.",
    )
    is_adjusted: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        doc="True if adjusted for corporate splits and cash dividends",
    )
    data_source: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default="demo_historical",
        doc="Provider lineage: demo_historical, polygon, bloomberg",
    )

    company = relationship("Company", back_populates="price_bars")

    __table_args__ = (
        Index("idx_price_bars_ticker_timestamp", "ticker", "timestamp", "interval", unique=True),
    )


class IncomeStatement(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    Normalized Income Statement Entity.
    Represents audited accounting revenue, expenses, and profitability metrics.
    """

    __tablename__ = "income_statements"

    ticker: Mapped[str] = mapped_column(
        String(16),
        ForeignKey("companies.ticker", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    period: Mapped[str] = mapped_column(
        String(16),
        nullable=False,
        doc="Reporting period: e.g. 2024, 2024-Q3, TTM",
    )
    period_type: Mapped[str] = mapped_column(
        String(16),
        nullable=False,
        default="ANNUAL",
        doc="Period classification: ANNUAL, QUARTERLY, TTM",
    )
    filing_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        doc="Official SEC / regulatory publication date (prevents look-ahead bias)",
    )
    currency: Mapped[str] = mapped_column(
        String(8),
        nullable=False,
        default="USD",
    )

    # Core Reported Line Items (Monetary precision)
    revenue: Mapped[Decimal] = mapped_column(Numeric(MONETARY_PRECISION, MONETARY_SCALE), nullable=False)
    cost_of_revenue: Mapped[Decimal] = mapped_column(Numeric(MONETARY_PRECISION, MONETARY_SCALE), nullable=False)
    gross_profit: Mapped[Decimal] = mapped_column(Numeric(MONETARY_PRECISION, MONETARY_SCALE), nullable=False)
    operating_expenses: Mapped[Decimal] = mapped_column(Numeric(MONETARY_PRECISION, MONETARY_SCALE), nullable=False)
    operating_income: Mapped[Decimal] = mapped_column(Numeric(MONETARY_PRECISION, MONETARY_SCALE), nullable=False)
    ebitda: Mapped[Decimal] = mapped_column(Numeric(MONETARY_PRECISION, MONETARY_SCALE), nullable=False)
    ebit: Mapped[Decimal] = mapped_column(Numeric(MONETARY_PRECISION, MONETARY_SCALE), nullable=False)
    interest_expense: Mapped[Decimal] = mapped_column(Numeric(MONETARY_PRECISION, MONETARY_SCALE), nullable=False)
    pre_tax_income: Mapped[Decimal] = mapped_column(Numeric(MONETARY_PRECISION, MONETARY_SCALE), nullable=False)
    tax_expense: Mapped[Decimal] = mapped_column(Numeric(MONETARY_PRECISION, MONETARY_SCALE), nullable=False)
    net_income: Mapped[Decimal] = mapped_column(Numeric(MONETARY_PRECISION, MONETARY_SCALE), nullable=False)

    # Per Share Metrics
    eps: Mapped[Decimal] = mapped_column(Numeric(10, 4), nullable=True)
    diluted_eps: Mapped[Decimal] = mapped_column(Numeric(10, 4), nullable=True)

    # Audit & Provenance Metadata
    source: Mapped[str] = mapped_column(String(32), nullable=False, default="SEC_EDGAR")
    data_version: Mapped[str] = mapped_column(String(16), nullable=False, default="v1.0")
    quality_status: Mapped[str] = mapped_column(String(16), nullable=False, default="VERIFIED")
    is_synthetic: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    company = relationship("Company", back_populates="income_statements")

    __table_args__ = (
        Index("idx_income_stmt_ticker_period", "ticker", "period", "period_type", unique=True),
    )


class BalanceSheet(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    Normalized Balance Sheet Entity.
    Represents point-in-time assets, liabilities, and shareholder equity.
    """

    __tablename__ = "balance_sheets"

    ticker: Mapped[str] = mapped_column(
        String(16),
        ForeignKey("companies.ticker", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    period: Mapped[str] = mapped_column(String(16), nullable=False)
    period_type: Mapped[str] = mapped_column(String(16), nullable=False, default="ANNUAL")
    filing_date: Mapped[date] = mapped_column(Date, nullable=False)
    currency: Mapped[str] = mapped_column(String(8), nullable=False, default="USD")

    # Assets
    cash_and_equivalents: Mapped[Decimal] = mapped_column(Numeric(MONETARY_PRECISION, MONETARY_SCALE), nullable=False)
    short_term_investments: Mapped[Decimal] = mapped_column(Numeric(MONETARY_PRECISION, MONETARY_SCALE), nullable=False, default=0)
    current_assets: Mapped[Decimal] = mapped_column(Numeric(MONETARY_PRECISION, MONETARY_SCALE), nullable=False)
    goodwill: Mapped[Decimal] = mapped_column(Numeric(MONETARY_PRECISION, MONETARY_SCALE), nullable=False, default=0)
    intangible_assets: Mapped[Decimal] = mapped_column(Numeric(MONETARY_PRECISION, MONETARY_SCALE), nullable=False, default=0)
    total_assets: Mapped[Decimal] = mapped_column(Numeric(MONETARY_PRECISION, MONETARY_SCALE), nullable=False)

    # Liabilities
    current_liabilities: Mapped[Decimal] = mapped_column(Numeric(MONETARY_PRECISION, MONETARY_SCALE), nullable=False)
    short_term_debt: Mapped[Decimal] = mapped_column(Numeric(MONETARY_PRECISION, MONETARY_SCALE), nullable=False, default=0)
    long_term_debt: Mapped[Decimal] = mapped_column(Numeric(MONETARY_PRECISION, MONETARY_SCALE), nullable=False, default=0)
    total_debt: Mapped[Decimal] = mapped_column(Numeric(MONETARY_PRECISION, MONETARY_SCALE), nullable=False)
    total_liabilities: Mapped[Decimal] = mapped_column(Numeric(MONETARY_PRECISION, MONETARY_SCALE), nullable=False)

    # Equity
    shareholders_equity: Mapped[Decimal] = mapped_column(Numeric(MONETARY_PRECISION, MONETARY_SCALE), nullable=False)

    # Audit & Lineage
    source: Mapped[str] = mapped_column(String(32), nullable=False, default="SEC_EDGAR")
    data_version: Mapped[str] = mapped_column(String(16), nullable=False, default="v1.0")
    quality_status: Mapped[str] = mapped_column(String(16), nullable=False, default="VERIFIED")
    is_synthetic: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    company = relationship("Company", back_populates="balance_sheets")

    __table_args__ = (
        Index("idx_balance_sheet_ticker_period", "ticker", "period", "period_type", unique=True),
    )


class CashFlowStatement(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    Normalized Cash Flow Statement Entity.
    Represents cash generation, capital deployment, and financing flows.
    """

    __tablename__ = "cash_flow_statements"

    ticker: Mapped[str] = mapped_column(
        String(16),
        ForeignKey("companies.ticker", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    period: Mapped[str] = mapped_column(String(16), nullable=False)
    period_type: Mapped[str] = mapped_column(String(16), nullable=False, default="ANNUAL")
    filing_date: Mapped[date] = mapped_column(Date, nullable=False)
    currency: Mapped[str] = mapped_column(String(8), nullable=False, default="USD")

    # Core Reported Cash Flow Lines
    operating_cash_flow: Mapped[Decimal] = mapped_column(Numeric(MONETARY_PRECISION, MONETARY_SCALE), nullable=False)
    capital_expenditure: Mapped[Decimal] = mapped_column(Numeric(MONETARY_PRECISION, MONETARY_SCALE), nullable=False)
    investing_cash_flow: Mapped[Decimal] = mapped_column(Numeric(MONETARY_PRECISION, MONETARY_SCALE), nullable=False)
    financing_cash_flow: Mapped[Decimal] = mapped_column(Numeric(MONETARY_PRECISION, MONETARY_SCALE), nullable=False)
    free_cash_flow: Mapped[Decimal] = mapped_column(Numeric(MONETARY_PRECISION, MONETARY_SCALE), nullable=False)

    # Audit & Lineage
    source: Mapped[str] = mapped_column(String(32), nullable=False, default="SEC_EDGAR")
    data_version: Mapped[str] = mapped_column(String(16), nullable=False, default="v1.0")
    quality_status: Mapped[str] = mapped_column(String(16), nullable=False, default="VERIFIED")
    is_synthetic: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    company = relationship("Company", back_populates="cash_flow_statements")

    __table_args__ = (
        Index("idx_cash_flow_ticker_period", "ticker", "period", "period_type", unique=True),
    )
