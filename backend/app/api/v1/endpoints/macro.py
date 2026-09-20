"""
AEGIS INVEST — Macroeconomic API Endpoints
Provides sovereign economic series, yield curve inversion metrics, and asset macro sensitivities.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.schemas.macro import (
    AssetMacroSensitivityOut,
    MacroSeriesOut,
    YieldCurveResponse,
)
from app.services.macro_service import MacroService

router = APIRouter(prefix="/macro", tags=["Macroeconomic Intelligence"])


@router.get(
    "/series",
    response_model=List[MacroSeriesOut],
    status_code=status.HTTP_200_OK,
    summary="List Macro Series",
    description="Returns metadata and latest values for all tracked sovereign macroeconomic time series.",
)
async def list_macro_series(
    db: AsyncSession = Depends(get_db),
) -> List[MacroSeriesOut]:
    service = MacroService(db)
    return await service.list_series()


@router.get(
    "/series/{series_code}",
    response_model=MacroSeriesOut,
    status_code=status.HTTP_200_OK,
    summary="Macro Series Observations",
    description="Returns historical observations and metadata for a specific economic series (e.g. FEDFUNDS, DGS10, CPI_YOY).",
)
async def get_series_detail(
    series_code: str,
    limit: int = Query(100, ge=5, le=500),
    db: AsyncSession = Depends(get_db),
) -> MacroSeriesOut:
    service = MacroService(db)
    res = await service.get_series_detail(series_code, limit=limit)
    if not res:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Macroeconomic series '{series_code}' not found",
        )
    return res


@router.get(
    "/yield-curve",
    response_model=YieldCurveResponse,
    status_code=status.HTTP_200_OK,
    summary="Sovereign Yield Curve",
    description="Returns US Treasury yield curve structure (3M to 30Y) and 10Y-2Y inversion spread metrics.",
)
async def get_yield_curve(
    db: AsyncSession = Depends(get_db),
) -> YieldCurveResponse:
    service = MacroService(db)
    return await service.get_yield_curve()


@router.get(
    "/sensitivity/{ticker}",
    response_model=AssetMacroSensitivityOut,
    status_code=status.HTTP_200_OK,
    summary="Asset Macro Sensitivity Profile",
    description="Computes statistical sensitivities, betas, correlations, and resilience scores of an equity asset across macro variables.",
)
async def get_asset_macro_sensitivity(
    ticker: str,
    db: AsyncSession = Depends(get_db),
) -> AssetMacroSensitivityOut:
    service = MacroService(db)
    return await service.get_asset_sensitivity(ticker)
