"""
AEGIS INVEST — News Domain Models
Defines persistent entities for News Articles, Extracted Entities, and Event Classifications.
Includes content hashing for deduplication and strict provenance metadata.
"""

from datetime import datetime
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin, utc_now


class NewsArticle(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    Standardized financial news article representation.
    Guarantees deduplication via SHA-256 content_hash.
    """
    __tablename__ = "news_articles"

    headline: Mapped[str] = mapped_column(String(500), nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=True)
    publisher: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    source: Mapped[str] = mapped_column(String(100), nullable=False, default="SEC_EDGAR_DEMO")
    url: Mapped[str] = mapped_column(String(1000), nullable=True)
    published_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    retrieved_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now)

    company_id: Mapped[str] = mapped_column(String(36), nullable=True, index=True)
    ticker: Mapped[str] = mapped_column(String(20), nullable=True, index=True)
    sector: Mapped[str] = mapped_column(String(100), nullable=True, index=True)
    industry: Mapped[str] = mapped_column(String(100), nullable=True)
    country: Mapped[str] = mapped_column(String(50), nullable=False, default="USA")

    category: Mapped[str] = mapped_column(
        String(50), nullable=False, default="UNKNOWN", index=True
    )  # EARNINGS, M&A, MANAGEMENT, REGULATION, PRODUCT, LEGAL, MACRO, SUPPLY_CHAIN, GUIDANCE, CAPITAL_ALLOCATION, OTHER, UNKNOWN

    language: Mapped[str] = mapped_column(String(10), nullable=False, default="en")
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False, unique=True, index=True)

    data_source: Mapped[str] = mapped_column(String(50), nullable=False, default="demo_historical")
    data_version: Mapped[str] = mapped_column(String(20), nullable=False, default="1.0")
    quality_status: Mapped[str] = mapped_column(String(30), nullable=False, default="AUDITED")
    is_synthetic: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    # Relationships
    entities: Mapped[list["NewsEntity"]] = relationship(
        "NewsEntity", back_populates="article", cascade="all, delete-orphan", lazy="selectin"
    )
    events: Mapped[list["NewsEvent"]] = relationship(
        "NewsEvent", back_populates="article", cascade="all, delete-orphan", lazy="selectin"
    )

    __table_args__ = (
        Index("ix_news_ticker_published", "ticker", "published_at"),
        Index("ix_news_category_published", "category", "published_at"),
    )


class NewsEntity(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Extracted named entity associated with a news article."""
    __tablename__ = "news_entities"

    article_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("news_articles.id", ondelete="CASCADE"), nullable=False, index=True
    )
    entity_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # Company, Ticker, Person, Organization, Sector, Product, Currency
    entity_name: Mapped[str] = mapped_column(String(200), nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)

    article: Mapped["NewsArticle"] = relationship("NewsArticle", back_populates="entities")


class NewsEvent(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Categorized event extracted from financial news."""
    __tablename__ = "news_events"

    article_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("news_articles.id", ondelete="CASCADE"), nullable=False, index=True
    )
    event_type: Mapped[str] = mapped_column(
        String(50), nullable=False, index=True
    )  # Earnings Beat, Earnings Miss, Guidance Change, M&A, Leadership Change, Regulatory Action, Product Launch, Legal Event, Capital Allocation, Supply Chain Event, Macro Event
    event_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    details: Mapped[str] = mapped_column(Text, nullable=True)

    article: Mapped["NewsArticle"] = relationship("NewsArticle", back_populates="events")
