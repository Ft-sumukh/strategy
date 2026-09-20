"""
AEGIS INVEST — Research Workspace, Watchlists, Alerts & Model Registry Models
Defines persistent entities for analyst theses, watchlists, proactive alert triggers,
research reports, and ML/AI model monitoring.
"""

from datetime import datetime
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Index, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin, utc_now


class Watchlist(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """User-curated watchlist of securities."""
    __tablename__ = "watchlists"

    user_id: Mapped[str] = mapped_column(String(36), nullable=False, default="default_user", index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=True)
    display_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    items: Mapped[list["WatchlistItem"]] = relationship(
        "WatchlistItem", back_populates="watchlist", cascade="all, delete-orphan", lazy="selectin"
    )

    __table_args__ = (
        Index("ix_watchlist_user_name", "user_id", "name", unique=True),
    )


class WatchlistItem(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Individual security entry within a watchlist."""
    __tablename__ = "watchlist_items"

    watchlist_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("watchlists.id", ondelete="CASCADE"), nullable=False, index=True
    )
    ticker: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    target_price: Mapped[float] = mapped_column(Float, nullable=True)
    notes: Mapped[str] = mapped_column(Text, nullable=True)
    tags: Mapped[list] = mapped_column(JSON, nullable=False, default=list)

    watchlist: Mapped[Watchlist] = relationship("Watchlist", back_populates="items")

    __table_args__ = (
        Index("ix_item_watchlist_ticker", "watchlist_id", "ticker", unique=True),
    )


class AlertRule(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Proactive monitoring rule with threshold evaluation."""
    __tablename__ = "alert_rules"

    user_id: Mapped[str] = mapped_column(String(36), nullable=False, default="default_user", index=True)
    ticker: Mapped[str] = mapped_column(String(20), nullable=True, index=True)  # Null if portfolio/market level
    portfolio_id: Mapped[str] = mapped_column(String(36), nullable=True, index=True)
    alert_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # PRICE, VALUATION_PE, RSI, DRAWDOWN, REGIME_CHANGE, SENTIMENT_DROP, THESIS_INVALIDATION
    condition: Mapped[str] = mapped_column(String(20), nullable=False)  # GREATER_THAN, LESS_THAN, EQUALS, CHANGES_TO
    threshold: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="ACTIVE")  # ACTIVE, TRIGGERED, DISABLED
    notification_channel: Mapped[str] = mapped_column(String(30), nullable=False, default="IN_APP")
    last_triggered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)

    events: Mapped[list["AlertEvent"]] = relationship(
        "AlertEvent", back_populates="rule", cascade="all, delete-orphan", lazy="selectin"
    )


class AlertEvent(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Record of a triggered alert event."""
    __tablename__ = "alert_events"

    rule_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("alert_rules.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id: Mapped[str] = mapped_column(String(36), nullable=False, default="default_user", index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    observed_value: Mapped[str] = mapped_column(String(100), nullable=False)
    triggered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now)
    is_read: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    rule: Mapped[AlertRule] = relationship("AlertRule", back_populates="events")


class InvestmentThesis(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Institutional, versioned investment thesis with invalidation tracking."""
    __tablename__ = "investment_theses"

    user_id: Mapped[str] = mapped_column(String(36), nullable=False, default="default_user", index=True)
    ticker: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    investment_case: Mapped[str] = mapped_column(Text, nullable=False)
    time_horizon: Mapped[str] = mapped_column(String(50), nullable=False, default="1-3 Years")
    key_assumptions: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    supporting_evidence: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    contradicting_evidence: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    invalidation_conditions: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="ACTIVE")  # ACTIVE, DRAFT, INVALIDATED, ARCHIVED
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    versions: Mapped[list["ThesisVersion"]] = relationship(
        "ThesisVersion", back_populates="thesis", cascade="all, delete-orphan", lazy="selectin"
    )


class ThesisVersion(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Immutable historical revision of an investment thesis."""
    __tablename__ = "thesis_versions"

    thesis_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("investment_theses.id", ondelete="CASCADE"), nullable=False, index=True
    )
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    snapshot: Mapped[dict] = mapped_column(JSON, nullable=False)  # Full copy of title, summary, case, assumptions, evidence
    change_rationale: Mapped[str] = mapped_column(Text, nullable=True)

    thesis: Mapped[InvestmentThesis] = relationship("InvestmentThesis", back_populates="versions")

    __table_args__ = (
        Index("ix_thesis_ver_num", "thesis_id", "version_number", unique=True),
    )


class ResearchReport(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Structured analyst research report / memo."""
    __tablename__ = "research_reports"

    user_id: Mapped[str] = mapped_column(String(36), nullable=False, default="default_user", index=True)
    report_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # COMPANY, PORTFOLIO_RISK, STRATEGY, REGIME, STRESS_TEST, THESIS
    subject_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)  # Ticker, portfolio_id, strategy_key
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    executive_summary: Mapped[str] = mapped_column(Text, nullable=False)
    content_sections: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    evidence_citations: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    data_version: Mapped[str] = mapped_column(String(30), nullable=False, default="1.0")
    engine_versions: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    ai_model: Mapped[str] = mapped_column(String(60), nullable=False, default="aegis-institutional-v1")
    prompt_version: Mapped[str] = mapped_column(String(30), nullable=False, default="report_v1")


class ModelRegistryItem(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Registry and monitoring tracking of analytical and ML models."""
    __tablename__ = "model_registry"

    model_name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    model_type: Mapped[str] = mapped_column(String(50), nullable=False)  # VALUATION, TECHNICAL, FACTOR, REGIME, SENTIMENT, OPTIMIZATION
    version: Mapped[str] = mapped_column(String(30), nullable=False, default="1.0.0")
    provider: Mapped[str] = mapped_column(String(60), nullable=False, default="INTERNAL_DETERMINISTIC")
    training_period: Mapped[str] = mapped_column(String(100), nullable=True)
    feature_set: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    performance_metrics: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    drift_metrics: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="PRODUCTION")  # PRODUCTION, STAGING, DEPRECATED
