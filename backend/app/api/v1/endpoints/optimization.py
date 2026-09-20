"""
AEGIS INVEST — Portfolio Optimization REST Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.backtest import OptimizationRequestSchema
from app.services.optimization_service import OptimizationService

router = APIRouter(prefix="/optimization", tags=["Portfolio Optimization"])


@router.post("/run")
async def optimize_portfolio(payload: OptimizationRequestSchema, session: AsyncSession = Depends(get_db)):
    svc = OptimizationService(session)
    res = await svc.optimize_portfolio(
        portfolio_id=payload.portfolio_id,
        objective=payload.objective,
        min_weight=payload.min_weight,
        max_weight=payload.max_weight,
    )
    if "error" in res:
        raise HTTPException(status_code=404, detail=res["error"])
    return res
