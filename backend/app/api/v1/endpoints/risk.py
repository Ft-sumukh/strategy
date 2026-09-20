"""
AEGIS INVEST — Risk REST Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.services.risk_service import RiskService

router = APIRouter(prefix="/risk", tags=["Risk Analysis"])


@router.get("/portfolio/{portfolio_id}")
async def get_portfolio_risk(portfolio_id: str, session: AsyncSession = Depends(get_db)):
    svc = RiskService(session)
    res = await svc.get_portfolio_risk_profile(portfolio_id)
    if "error" in res:
        raise HTTPException(status_code=404, detail=res["error"])
    return res
