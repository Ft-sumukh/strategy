"""
AEGIS INVEST — News & Event Intelligence API Endpoints
Provides filtered news feeds, article lookups, and event extractions.
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.schemas.news import NewsArticleListResponse, NewsArticleOut
from app.services.news_service import NewsService

router = APIRouter(prefix="/news", tags=["News & Events"])


@router.get(
    "",
    response_model=NewsArticleListResponse,
    status_code=status.HTTP_200_OK,
    summary="List News Articles",
    description="Returns filtered and sanitized news articles with entity tags, event tags, and sentiment scores.",
)
async def list_news(
    ticker: Optional[str] = Query(None, description="Filter by asset ticker (e.g. AAPL)"),
    category: Optional[str] = Query(None, description="Filter by category (e.g. COMPANY_SPECIFIC, MACROECONOMIC)"),
    limit: int = Query(50, ge=1, le=100, description="Max articles to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    db: AsyncSession = Depends(get_db),
) -> NewsArticleListResponse:
    service = NewsService(db)
    return await service.list_articles(ticker=ticker, category=category, limit=limit, offset=offset)


@router.get(
    "/company/{ticker}",
    response_model=NewsArticleListResponse,
    status_code=status.HTTP_200_OK,
    summary="Company News Timeline",
    description="Returns audited news articles specifically tagged to the company.",
)
async def get_company_news(
    ticker: str,
    limit: int = Query(25, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
) -> NewsArticleListResponse:
    service = NewsService(db)
    return await service.list_articles(ticker=ticker, limit=limit)


@router.get(
    "/market",
    response_model=NewsArticleListResponse,
    status_code=status.HTTP_200_OK,
    summary="Market & Macro News",
    description="Returns macro and market-wide news articles.",
)
async def get_market_news(
    limit: int = Query(25, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
) -> NewsArticleListResponse:
    service = NewsService(db)
    return await service.list_articles(category="MACROECONOMIC", limit=limit)


@router.get(
    "/{article_id}",
    response_model=NewsArticleOut,
    status_code=status.HTTP_200_OK,
    summary="Get News Article by ID",
    description="Retrieves a single news article with full entity and event extractions.",
)
async def get_article(
    article_id: str,
    db: AsyncSession = Depends(get_db),
) -> NewsArticleOut:
    service = NewsService(db)
    article = await service.get_article_by_id(article_id)
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"News article not found with ID '{article_id}'",
        )
    return article
