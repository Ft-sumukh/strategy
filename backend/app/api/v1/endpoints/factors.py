"""
AEGIS INVEST — Quantitative Factors API Endpoints
Serves 7 institutional equity style factors:
Momentum, Value, Quality, Size, Low Volatility, Growth, Liquidity.
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.schemas.financials import FullFactorsResponse
from app.services.financial_service import FinancialIntelligenceService

router = APIRouter(prefix="/factors", tags=["Factors"])


@router.get(
    "/{ticker}",
    response_model=FullFactorsResponse,
    status_code=status.HTTP_200_OK,
    summary="Multi-Factor Equity Style Profile",
    description="Returns normalized 7-factor exposures, Z-scores, percentile ranks, and radar profile.",
)
async def get_factors(
    ticker: str,
    db: AsyncSession = Depends(get_db),
) -> FullFactorsResponse:
    service = FinancialIntelligenceService(db)
    return await service.get_factors(ticker)
