"""
AEGIS INVEST — Sentiment Analytics API Endpoints
Provides company, sector, and market sentiment, rolling momentum, and dispersion measurements.
"""

from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.schemas.sentiment import AggregatedSentimentOut, SectorSentimentOut
from app.services.sentiment_service import SentimentService

router = APIRouter(prefix="/sentiment", tags=["Sentiment Analytics"])


@router.get(
    "/company/{ticker}",
    response_model=AggregatedSentimentOut,
    status_code=status.HTTP_200_OK,
    summary="Company Sentiment & Momentum",
    description="Returns aggregated sentiment score, dispersion, and multi-window rolling momentum (1D, 7D, 30D, 90D) for a ticker.",
)
async def get_company_sentiment(
    ticker: str,
    db: AsyncSession = Depends(get_db),
) -> AggregatedSentimentOut:
    service = SentimentService(db)
    return await service.get_company_sentiment(ticker)


@router.get(
    "/market",
    response_model=AggregatedSentimentOut,
    status_code=status.HTTP_200_OK,
    summary="Market-Wide Sentiment & Momentum",
    description="Returns aggregate sentiment across all market news articles with multi-window momentum.",
)
async def get_market_sentiment(
    db: AsyncSession = Depends(get_db),
) -> AggregatedSentimentOut:
    service = SentimentService(db)
    return await service.get_market_sentiment()


@router.get(
    "/sectors",
    response_model=List[SectorSentimentOut],
    status_code=status.HTTP_200_OK,
    summary="Sector Sentiment Breakdown",
    description="Returns average sentiment scores, article counts, and 7-day momentum across market sectors.",
)
async def get_sector_sentiments(
    db: AsyncSession = Depends(get_db),
) -> List[SectorSentimentOut]:
    service = SentimentService(db)
    return await service.get_sector_sentiments()
