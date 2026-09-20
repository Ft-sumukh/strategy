"""
AEGIS INVEST — Stock Screener API Endpoints
Provides multi-factor filtering, sorting, and pagination across universe.
"""

from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.schemas.financials import ScreenerResponse
from app.services.financial_service import FinancialIntelligenceService

router = APIRouter(prefix="/screener", tags=["Screener"])


@router.get(
    "",
    response_model=ScreenerResponse,
    status_code=status.HTTP_200_OK,
    summary="Multi-Factor Stock Screener",
    description="Filters companies by sector, market cap, P/E ratio, FCF yield, and fundamental scorecard with sorting and pagination.",
)
async def screen_stocks(
    sector: Optional[str] = Query(None, description="Filter by sector (e.g. Technology, Consumer Cyclical)"),
    min_market_cap: Optional[float] = Query(None, description="Minimum market capitalization in USD"),
    max_market_cap: Optional[float] = Query(None, description="Maximum market capitalization in USD"),
    min_pe: Optional[float] = Query(None, description="Minimum P/E ratio"),
    max_pe: Optional[float] = Query(None, description="Maximum P/E ratio"),
    min_fcf_yield: Optional[float] = Query(None, description="Minimum Free Cash Flow Yield (e.g. 0.03 for 3%)"),
    min_scorecard: Optional[float] = Query(None, description="Minimum Fundamental Scorecard score (0 - 100)"),
    sort_by: str = Query("market_cap", description="Field to sort by (market_cap, pe_ratio, scorecard_score, fcf_yield, ticker)"),
    sort_direction: str = Query("desc", description="Sort direction ('asc' or 'desc')"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=100, description="Page size limit"),
    db: AsyncSession = Depends(get_db),
) -> ScreenerResponse:
    service = FinancialIntelligenceService(db)
    return await service.run_screener(
        sector=sector,
        min_market_cap=min_market_cap,
        max_market_cap=max_market_cap,
        min_pe=min_pe,
        max_pe=max_pe,
        min_fcf_yield=min_fcf_yield,
        min_scorecard=min_scorecard,
        sort_by=sort_by,
        sort_direction=sort_direction,
        page=page,
        limit=limit,
    )
