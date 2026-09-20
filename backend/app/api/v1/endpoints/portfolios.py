"""
AEGIS INVEST — Portfolio REST Endpoints
"""

from typing import Any, Dict, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.portfolio import PortfolioCreateSchema, PortfolioUpdateSchema
from app.services.portfolio_service import PortfolioService

router = APIRouter(prefix="/portfolios", tags=["Portfolio Management"])


@router.get("", response_model=List[Dict[str, Any]])
async def list_portfolios(session: AsyncSession = Depends(get_db)):
    svc = PortfolioService(session)
    portfolios = await svc.list_portfolios()
    result = []
    for p in portfolios:
        h_list = p.holdings if isinstance(p.holdings, list) else ([p.holdings] if p.holdings else [])
        result.append({
            "id": p.id,
            "name": p.name,
            "description": p.description,
            "user_id": p.user_id,
            "holdings_count": len(h_list),
            "holdings": [{"ticker": h.ticker, "weight": h.weight, "quantity": h.quantity, "cost_basis": h.cost_basis} for h in h_list],
            "total_weight": p.total_weight(),
            "created_at": p.created_at.isoformat() if p.created_at else "",
        })
    return result


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_portfolio(payload: PortfolioCreateSchema, session: AsyncSession = Depends(get_db)):
    svc = PortfolioService(session)
    holdings_data = [h.model_dump() for h in payload.holdings]
    p = await svc.create_portfolio(payload.name, payload.description, holdings_data)
    h_list = p.holdings if isinstance(p.holdings, list) else ([p.holdings] if p.holdings else [])
    return {
        "id": p.id,
        "name": p.name,
        "description": p.description,
        "holdings": [{"ticker": h.ticker, "weight": h.weight, "quantity": h.quantity, "cost_basis": h.cost_basis} for h in h_list],
        "total_weight": p.total_weight(),
    }


@router.get("/{portfolio_id}")
async def get_portfolio(portfolio_id: str, session: AsyncSession = Depends(get_db)):
    svc = PortfolioService(session)
    p = await svc.get_portfolio(portfolio_id)
    if not p:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    h_list = p.holdings if isinstance(p.holdings, list) else ([p.holdings] if p.holdings else [])
    return {
        "id": p.id,
        "name": p.name,
        "description": p.description,
        "user_id": p.user_id,
        "holdings": [{"ticker": h.ticker, "weight": h.weight, "quantity": h.quantity, "cost_basis": h.cost_basis} for h in h_list],
        "total_weight": p.total_weight(),
        "created_at": p.created_at.isoformat() if p.created_at else "",
    }


@router.get("/{portfolio_id}/analytics")
async def get_portfolio_analytics(portfolio_id: str, session: AsyncSession = Depends(get_db)):
    svc = PortfolioService(session)
    analytics = await svc.compute_portfolio_analytics(portfolio_id)
    if "error" in analytics:
        raise HTTPException(status_code=404, detail=analytics["error"])
    return analytics


@router.patch("/{portfolio_id}")
async def update_portfolio(portfolio_id: str, payload: PortfolioUpdateSchema, session: AsyncSession = Depends(get_db)):
    svc = PortfolioService(session)
    p = await svc.update_portfolio(portfolio_id, payload.name, payload.description)
    if not p:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    return {"id": p.id, "name": p.name, "description": p.description}


@router.delete("/{portfolio_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_portfolio(portfolio_id: str, session: AsyncSession = Depends(get_db)):
    svc = PortfolioService(session)
    success = await svc.delete_portfolio(portfolio_id)
    if not success:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    return None
