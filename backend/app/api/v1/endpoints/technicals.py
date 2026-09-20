"""
AEGIS INVEST — Technical Analysis API Endpoints
Serves moving averages (SMA, EMA), RSI 14, MACD, Bollinger Bands,
ATR 14, ADX 14, annualized volatility, momentum returns, and standardized signals.
"""

from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.schemas.financials import FullTechnicalsResponse, TechnicalSignalSchema
from app.services.financial_service import FinancialIntelligenceService

router = APIRouter(prefix="/technicals", tags=["Technicals"])


@router.get(
    "/{ticker}",
    response_model=FullTechnicalsResponse,
    status_code=status.HTTP_200_OK,
    summary="Complete Technical Analysis Profile",
    description="Returns moving averages, RSI 14, MACD, Bollinger Bands, ATR, ADX, and rule-based signals.",
)
async def get_technicals(
    ticker: str,
    db: AsyncSession = Depends(get_db),
) -> FullTechnicalsResponse:
    service = FinancialIntelligenceService(db)
    return await service.get_technicals(ticker)


@router.get(
    "/{ticker}/signals",
    response_model=List[TechnicalSignalSchema],
    status_code=status.HTTP_200_OK,
    summary="Standardized Technical Signals",
    description="Returns array of deterministic technical signal objects with indicator values, benchmarks, and rationales.",
)
async def get_technical_signals(
    ticker: str,
    db: AsyncSession = Depends(get_db),
) -> List[TechnicalSignalSchema]:
    service = FinancialIntelligenceService(db)
    res = await service.get_technicals(ticker)
    return res.signals
