"""
AEGIS INVEST — Market Regime API Endpoints
Provides multi-signal current regime classification and audited historical regime timelines.
"""

from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.schemas.regime import HistoricalRegimePeriodOut, RegimeEvaluationOut
from app.services.regime_service import RegimeService

router = APIRouter(prefix="/regime", tags=["Market Regime"])


@router.get(
    "/current",
    response_model=RegimeEvaluationOut,
    status_code=status.HTTP_200_OK,
    summary="Current Market Regime",
    description="Evaluates current market regime synthesized across trend, momentum, volatility, breadth, and credit spreads.",
)
async def get_current_regime(
    db: AsyncSession = Depends(get_db),
) -> RegimeEvaluationOut:
    service = RegimeService(db)
    return await service.get_current_regime()


@router.get(
    "/history",
    response_model=List[HistoricalRegimePeriodOut],
    status_code=status.HTTP_200_OK,
    summary="Historical Regime Timeline",
    description="Returns audited historical market regime timeline and transition drivers.",
)
async def get_regime_history(
    db: AsyncSession = Depends(get_db),
) -> List[HistoricalRegimePeriodOut]:
    service = RegimeService(db)
    return await service.get_regime_history()
