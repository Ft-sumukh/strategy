"""
AEGIS INVEST — Valuation API Endpoints
Serves valuation multiples (P/E, EV/EBITDA, P/S, P/B, FCF Yield),
historical percentiles, relative peer comparison, and DCF intrinsic value
models with 2D sensitivity matrices.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.schemas.financials import (
    DCFCalculationRequest,
    DCFModelResultSchema,
    FullValuationResponse,
    MultipleHistoricalContextSchema,
)
from app.services.financial_service import FinancialIntelligenceService

router = APIRouter(prefix="/valuation", tags=["Valuation"])


@router.get(
    "/{ticker}",
    response_model=FullValuationResponse,
    status_code=status.HTTP_200_OK,
    summary="Complete Valuation Profile",
    description="Returns current multiples, 3-year historical context, peer comparison, and DCF model with sensitivity grid.",
)
async def get_valuation(
    ticker: str,
    db: AsyncSession = Depends(get_db),
) -> FullValuationResponse:
    service = FinancialIntelligenceService(db)
    return await service.get_valuation(ticker)


@router.get(
    "/{ticker}/history",
    response_model=List[MultipleHistoricalContextSchema],
    status_code=status.HTTP_200_OK,
    summary="Historical Valuation Multiples Context",
    description="Returns 1Y/3Y/5Y medians, ranges, and percentile rankings for core multiples.",
)
async def get_valuation_history(
    ticker: str,
    db: AsyncSession = Depends(get_db),
) -> List[MultipleHistoricalContextSchema]:
    service = FinancialIntelligenceService(db)
    val = await service.get_valuation(ticker)
    return val.historical_context


@router.post(
    "/{ticker}/dcf",
    response_model=DCFModelResultSchema,
    status_code=status.HTTP_200_OK,
    summary="Interactive DCF Model & Sensitivity Analysis",
    description="Calculates 5-year FCFF DCF intrinsic value and 2D WACC x Terminal Growth sensitivity matrix with user assumptions.",
)
async def calculate_dcf(
    ticker: str,
    request: DCFCalculationRequest,
    db: AsyncSession = Depends(get_db),
) -> DCFModelResultSchema:
    service = FinancialIntelligenceService(db)
    val = await service.get_valuation(ticker, dcf_params=request)
    return val.dcf


@router.get(
    "/{ticker}/dcf",
    response_model=DCFModelResultSchema,
    status_code=status.HTTP_200_OK,
    summary="Default DCF Model & Sensitivity Analysis",
    description="Calculates 5-year FCFF DCF intrinsic value and sensitivity matrix using default institutional parameters.",
)
async def get_default_dcf(
    ticker: str,
    db: AsyncSession = Depends(get_db),
) -> DCFModelResultSchema:
    service = FinancialIntelligenceService(db)
    val = await service.get_valuation(ticker)
    return val.dcf
