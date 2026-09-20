"""
AEGIS INVEST — News & Event Intelligence Domain Service
Manages news ingestion, text sanitization, entity & event extraction,
and news article queries with strict untrusted external input defense (§ 18).
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.analytics.news.pipeline import NewsProcessingPipeline, ProcessedArticle
from app.analytics.sentiment.engine import SentimentEngine
from app.models.news import NewsArticle, NewsEntity, NewsEvent
from app.models.sentiment import SentimentRecord
from app.providers.news.provider import DemoNewsProvider
from app.schemas.news import (
    NewsArticleListResponse,
    NewsArticleOut,
    NewsEntityOut,
    NewsEventOut,
)


class NewsService:
    """Domain service for news articles, event intelligence, and entities."""

    def __init__(self, session: Optional[AsyncSession] = None):
        self.session = session
        self.pipeline = NewsProcessingPipeline()
        self.sentiment_engine = SentimentEngine()
        self.demo_provider = DemoNewsProvider()

    async def get_article_by_id(self, article_id: str) -> Optional[NewsArticleOut]:
        """Retrieves a single article by its unique ID."""
        if self.session:
            stmt = select(NewsArticle).where(NewsArticle.id == article_id)
            result = await self.session.execute(stmt)
            article = result.scalar_one_or_none()
            if article:
                return self._model_to_schema(article)

        # Fallback to demo provider
        demo_article = self.demo_provider.get_article_by_id(article_id)
        if demo_article:
            return self._dict_to_schema(demo_article)
        return None

    async def list_articles(
        self,
        ticker: Optional[str] = None,
        category: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> NewsArticleListResponse:
        """Queries articles with optional ticker and category filters."""
        # Query DB if available
        if self.session:
            query = select(NewsArticle).order_by(desc(NewsArticle.published_at))
            if ticker:
                query = query.where(NewsArticle.ticker == ticker.upper())
            if category:
                query = query.where(NewsArticle.category == category.upper())

            query = query.offset(offset).limit(limit)
            result = await self.session.execute(query)
            db_articles = result.scalars().all()

            if db_articles:
                items = [self._model_to_schema(a) for a in db_articles]
                return NewsArticleListResponse(
                    items=items,
                    total=len(items),
                    ticker=ticker.upper() if ticker else None,
                    category=category.upper() if category else None,
                )

        # Fallback to provider articles
        provider_articles = self.demo_provider.get_articles(ticker=ticker, category=category, limit=limit)
        items = [self._dict_to_schema(a) for a in provider_articles]
        return NewsArticleListResponse(
            items=items,
            total=len(items),
            ticker=ticker.upper() if ticker else None,
            category=category.upper() if category else None,
        )

    def _model_to_schema(self, a: NewsArticle) -> NewsArticleOut:
        entities = [
            NewsEntityOut(
                entity_type=e.entity_type,
                entity_name=e.entity_name,
                confidence=e.confidence,
            )
            for e in (a.entities or [])
        ]
        events = [
            NewsEventOut(
                event_type=ev.event_type,
                event_date=ev.event_date.isoformat() if ev.event_date else None,
                confidence=ev.confidence,
            )
            for ev in (a.events or [])
        ]
        return NewsArticleOut(
            id=str(a.id),
            headline=a.headline,
            summary=a.summary,
            content=a.content,
            publisher=a.publisher,
            source=a.source,
            url=a.url,
            published_at=a.published_at,
            ticker=a.ticker,
            sector=a.sector,
            industry=a.industry,
            country=a.country,
            category=a.category,
            language=a.language,
            content_hash=a.content_hash,
            sentiment_score=a.sentiment_score,
            sentiment=a.sentiment,
            entities=entities,
            events=events,
            is_synthetic=a.is_synthetic,
        )

    def _dict_to_schema(self, d: Dict[str, Any]) -> NewsArticleOut:
        entities = [
            NewsEntityOut(
                entity_type=e.get("entity_type", "Company"),
                entity_name=e.get("entity_name", ""),
                confidence=e.get("confidence", 0.9),
            )
            for e in d.get("entities", [])
        ]
        events = [
            NewsEventOut(
                event_type=ev.get("event_type", "MARKET_EVENT"),
                event_date=ev.get("event_date"),
                confidence=ev.get("confidence", 0.9),
            )
            for ev in d.get("events", [])
        ]
        dt = d.get("published_at")
        if isinstance(dt, str):
            try:
                dt = datetime.fromisoformat(dt.replace("Z", "+00:00"))
            except Exception:
                dt = datetime.now(timezone.utc)
        elif not isinstance(dt, datetime):
            dt = datetime.now(timezone.utc)

        return NewsArticleOut(
            id=str(d.get("id", "")),
            headline=d.get("headline", ""),
            summary=d.get("summary"),
            content=d.get("content"),
            publisher=d.get("publisher"),
            source=d.get("source"),
            url=d.get("url"),
            published_at=dt,
            ticker=d.get("ticker"),
            sector=d.get("sector"),
            industry=d.get("industry"),
            country=d.get("country"),
            category=d.get("category", "COMPANY_SPECIFIC"),
            language=d.get("language", "en"),
            content_hash=d.get("content_hash", ""),
            sentiment_score=d.get("sentiment_score"),
            sentiment=d.get("sentiment"),
            entities=entities,
            events=events,
            is_synthetic=d.get("is_synthetic", True),
        )
