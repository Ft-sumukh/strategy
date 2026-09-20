"""
AEGIS INVEST — Consolidated Stock Intelligence API Endpoints
Aggregates fundamentals, valuation, technicals, and quantitative factors
into a single consolidated company intelligence payload.
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.schemas.financials import CompanyIntelligenceResponse
from app.services.financial_service import FinancialIntelligenceService

router = APIRouter(prefix="/stocks", tags=["Stocks"])


@router.get(
    "/{ticker}/intelligence",
    response_model=CompanyIntelligenceResponse,
    status_code=status.HTTP_200_OK,
    summary="Consolidated Company Intelligence",
    description="Returns integrated company overview including live price stats, fundamental scorecard, valuation multiples, technical summary, factor radar, and provenance tags.",
)
async def get_stock_intelligence(
    ticker: str,
    db: AsyncSession = Depends(get_db),
) -> CompanyIntelligenceResponse:
    service = FinancialIntelligenceService(db)
    return await service.get_company_intelligence(ticker)
