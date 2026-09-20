"""
AEGIS INVEST — Sentiment Domain Service
Orchestrates article-level sentiment aggregation, momentum calculation (1D, 7D, 30D, 90D),
dispersion measurement, and sector/market sentiment profiles.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.analytics.sentiment.engine import SentimentEngine
from app.models.news import NewsArticle
from app.providers.news.provider import DemoNewsProvider
from app.schemas.sentiment import (
    AggregatedSentimentOut,
    SectorSentimentOut,
    SentimentMomentumDetail,
)


class SentimentService:
    """Domain service for financial sentiment, momentum, and dispersion."""

    SECTOR_MAPPING: Dict[str, str] = {
        "AAPL": "Technology",
        "MSFT": "Technology",
        "NVDA": "Technology",
        "GOOG": "Communication Services",
        "AMZN": "Consumer Discretionary",
    }

    def __init__(self, session: Optional[AsyncSession] = None):
        self.session = session
        self.engine = SentimentEngine()
        self.demo_provider = DemoNewsProvider()

    async def get_company_sentiment(self, ticker: str) -> AggregatedSentimentOut:
        """Retrieves aggregated sentiment and momentum metrics for a ticker."""
        ticker_upper = ticker.upper()
        # Fetch articles
        articles = await self._fetch_articles_for_ticker(ticker_upper)

        if not articles:
            # Generate baseline neutral
            return AggregatedSentimentOut(
                entity_type="COMPANY",
                entity_id=ticker_upper,
                headline_sentiment="NEUTRAL",
                current_score=0.0,
                dispersion=0.0,
                momentum_metrics={
                    w: SentimentMomentumDetail(
                        window=w, current_sentiment=0.0, historical_average=0.0,
                        change=0.0, dispersion=0.0, article_count=0
                    )
                    for w in ["1D", "7D", "30D", "90D"]
                },
                as_of_date=datetime.now(timezone.utc).isoformat(),
            )

        agg = self.engine.aggregate_sentiment(articles, entity_type="COMPANY", entity_id=ticker_upper)

        momentum_dict = {
            w: SentimentMomentumDetail(
                window=m.window,
                current_sentiment=m.current_sentiment,
                historical_average=m.historical_average,
                change=m.change,
                dispersion=m.dispersion,
                article_count=m.article_count,
            )
            for w, m in agg.momentum_metrics.items()
        }

        return AggregatedSentimentOut(
            entity_type=agg.entity_type,
            entity_id=agg.entity_id,
            headline_sentiment=agg.headline_sentiment,
            current_score=agg.current_score,
            dispersion=agg.dispersion,
            momentum_metrics=momentum_dict,
            as_of_date=agg.as_of_date,
        )

    async def get_market_sentiment(self) -> AggregatedSentimentOut:
        """Retrieves market-wide aggregated sentiment."""
        all_articles = await self._fetch_all_articles()
        agg = self.engine.aggregate_sentiment(all_articles, entity_type="MARKET", entity_id="MARKET")

        momentum_dict = {
            w: SentimentMomentumDetail(
                window=m.window,
                current_sentiment=m.current_sentiment,
                historical_average=m.historical_average,
                change=m.change,
                dispersion=m.dispersion,
                article_count=m.article_count,
            )
            for w, m in agg.momentum_metrics.items()
        }

        return AggregatedSentimentOut(
            entity_type="MARKET",
            entity_id="MARKET",
            headline_sentiment=agg.headline_sentiment,
            current_score=agg.current_score,
            dispersion=agg.dispersion,
            momentum_metrics=momentum_dict,
            as_of_date=agg.as_of_date,
        )

    async def get_sector_sentiments(self) -> List[SectorSentimentOut]:
        """Retrieves sentiment breakdown across primary economic sectors."""
        all_articles = await self._fetch_all_articles()

        # Group by sector
        sector_articles: Dict[str, List[Dict[str, Any]]] = {}
        for a in all_articles:
            sec = a.get("sector")
            if not sec:
                ticker = a.get("ticker", "")
                sec = self.SECTOR_MAPPING.get(ticker, "General")
            if sec not in sector_articles:
                sector_articles[sec] = []
            sector_articles[sec].append(a)

        results: List[SectorSentimentOut] = []
        for sec, arts in sector_articles.items():
            scores = [a.get("sentiment_score", 0.0) for a in arts if a.get("sentiment_score") is not None]
            avg_score = round(sum(scores) / len(scores), 2) if scores else 0.0
            sentiment_label = "POSITIVE" if avg_score >= 0.15 else ("NEGATIVE" if avg_score <= -0.15 else "NEUTRAL")

            results.append(
                SectorSentimentOut(
                    sector=sec,
                    score=avg_score,
                    sentiment=sentiment_label,
                    article_count=len(arts),
                    momentum_7d=round(avg_score * 0.4, 2),
                )
            )

        results.sort(key=lambda s: s.score, reverse=True)
        return results

    async def _fetch_articles_for_ticker(self, ticker: str) -> List[Dict[str, Any]]:
        if self.session:
            stmt = (
                select(NewsArticle)
                .where(NewsArticle.ticker == ticker)
                .order_by(desc(NewsArticle.published_at))
            )
            res = await self.session.execute(stmt)
            records = res.scalars().all()
            if records:
                return [
                    {
                        "headline": r.headline,
                        "sentiment_score": r.sentiment_score,
                        "published_at": r.published_at.isoformat(),
                        "ticker": r.ticker,
                        "sector": r.sector,
                    }
                    for r in records
                ]

        # Fallback to demo provider
        return self.demo_provider.get_articles(ticker=ticker)

    async def _fetch_all_articles(self) -> List[Dict[str, Any]]:
        if self.session:
            stmt = select(NewsArticle).order_by(desc(NewsArticle.published_at)).limit(100)
            res = await self.session.execute(stmt)
            records = res.scalars().all()
            if records:
                return [
                    {
                        "headline": r.headline,
                        "sentiment_score": r.sentiment_score,
                        "published_at": r.published_at.isoformat(),
                        "ticker": r.ticker,
                        "sector": r.sector,
                    }
                    for r in records
                ]

        return self.demo_provider.get_articles(limit=100)
