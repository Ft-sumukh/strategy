"""
AEGIS INVEST — Sentiment Domain Models
Defines persistent entities for article-level sentiment classifications
and multi-window aggregated sentiment metrics (Company, Sector, Market).
"""

from datetime import datetime
from sqlalchemy import DateTime, Float, ForeignKey, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin, utc_now


class SentimentRecord(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Article-level sentiment classification."""
    __tablename__ = "sentiment_records"

    article_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("news_articles.id", ondelete="CASCADE"), nullable=False, unique=True, index=True
    )
    ticker: Mapped[str] = mapped_column(String(20), nullable=True, index=True)
    sentiment: Mapped[str] = mapped_column(
        String(20), nullable=False
    )  # POSITIVE, NEUTRAL, NEGATIVE
    sentiment_score: Mapped[float] = mapped_column(
        Float, nullable=False
    )  # -1.0 (very negative) to +1.0 (very positive)
    confidence: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    model_version: Mapped[str] = mapped_column(String(50), nullable=False, default="lexicon_v1")
    processed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now)


class AggregateSentiment(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    Rolling window aggregate sentiment snapshot for companies, sectors, or the broader market.
    Supports 1D, 7D, 30D, and 90D horizons.
    """
    __tablename__ = "aggregate_sentiments"

    entity_type: Mapped[str] = mapped_column(String(20), nullable=False, index=True)  # COMPANY, SECTOR, MARKET
    entity_id: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # e.g. AAPL, Technology, MARKET
    period: Mapped[str] = mapped_column(String(10), nullable=False, index=True)  # 1D, 7D, 30D, 90D

    score: Mapped[float] = mapped_column(Float, nullable=False)  # -1.0 to 1.0
    dispersion: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)  # Variance across articles
    momentum: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)  # Rate of change vs prior window
    article_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    as_of_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)

    __table_args__ = (
        Index("ix_agg_sentiment_lookup", "entity_type", "entity_id", "period", "as_of_date"),
    )
