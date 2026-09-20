"""
AEGIS INVEST — Backtesting REST Endpoints
"""

from datetime import datetime, timezone
from typing import Any, Dict, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.backtest import BacktestRequestSchema
from app.services.backtest_service import BacktestService

router = APIRouter(prefix="/backtesting", tags=["Backtesting"])


@router.get("")
async def list_backtests(session: AsyncSession = Depends(get_db)):
    svc = BacktestService(session)
    return await svc.list_backtests()


@router.post("/run", status_code=status.HTTP_200_OK)
async def run_backtest(payload: BacktestRequestSchema, session: AsyncSession = Depends(get_db)):
    svc = BacktestService(session)
    s_date = datetime.fromisoformat(payload.start_date).replace(tzinfo=timezone.utc)
    e_date = datetime.fromisoformat(payload.end_date).replace(tzinfo=timezone.utc)

    res = await svc.run_backtest(
        name=payload.name,
        strategy_key=payload.strategy_key,
        universe=payload.universe,
        start_date=s_date,
        end_date=e_date,
        initial_capital=payload.initial_capital,
        rebalance_frequency=payload.rebalance_frequency,
        transaction_cost_bps=payload.transaction_cost_bps,
        slippage_bps=payload.slippage_bps,
        max_position_weight=payload.max_position_weight,
    )
    return res
