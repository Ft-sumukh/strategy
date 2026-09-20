"""
AEGIS INVEST — Portfolio Domain Service
Manages user portfolio lifecycle, holding allocation updates, weight constraints,
and performance snapshot history.
"""

from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional
import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.analytics.portfolio.engine import PortfolioAnalyticsEngine
from app.models.portfolio_models import Portfolio, PortfolioHolding, PortfolioSnapshot
from app.services.market_provider import get_market_data_provider


class PortfolioService:
    """Domain service for portfolio management."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.engine = PortfolioAnalyticsEngine()

    async def list_portfolios(self, user_id: str = "default_user") -> List[Portfolio]:
        stmt = (
            select(Portfolio)
            .where(Portfolio.user_id == user_id)
            .options(selectinload(Portfolio.holdings), selectinload(Portfolio.snapshots))
            .order_by(Portfolio.created_at.desc())
        )
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def get_portfolio(self, portfolio_id: str, user_id: str = "default_user") -> Optional[Portfolio]:
        stmt = (
            select(Portfolio)
            .where(Portfolio.id == portfolio_id, Portfolio.user_id == user_id)
            .options(selectinload(Portfolio.holdings), selectinload(Portfolio.snapshots))
        )
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def create_portfolio(
        self,
        name: str,
        description: Optional[str] = None,
        holdings_data: Optional[List[Dict[str, Any]]] = None,
        user_id: str = "default_user",
    ) -> Portfolio:
        portfolio = Portfolio(
            name=name,
            description=description,
            user_id=user_id,
        )
        self.session.add(portfolio)
        await self.session.flush()

        if holdings_data:
            for h in holdings_data:
                holding = PortfolioHolding(
                    portfolio_id=portfolio.id,
                    ticker=h["ticker"].upper(),
                    weight=float(h.get("weight", 0.0)),
                    quantity=int(h.get("quantity", 0)),
                    cost_basis=float(h.get("cost_basis", 0.0)),
                    commission_rate=float(h.get("commission_rate", 0.001)),
                    slippage_percent=float(h.get("slippage_percent", 0.0005)),
                )
                self.session.add(holding)

        await self.session.commit()
        return await self.get_portfolio(portfolio.id, user_id)  # type: ignore

    async def update_portfolio(
        self,
        portfolio_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        user_id: str = "default_user",
    ) -> Optional[Portfolio]:
        portfolio = await self.get_portfolio(portfolio_id, user_id)
        if not portfolio:
            return None
        if name is not None:
            portfolio.name = name
        if description is not None:
            portfolio.description = description
        await self.session.commit()
        return portfolio

    async def delete_portfolio(self, portfolio_id: str, user_id: str = "default_user") -> bool:
        portfolio = await self.get_portfolio(portfolio_id, user_id)
        if not portfolio:
            return False
        await self.session.delete(portfolio)
        await self.session.commit()
        return True

    async def compute_portfolio_analytics(self, portfolio_id: str, user_id: str = "default_user") -> Dict[str, Any]:
        portfolio = await self.get_portfolio(portfolio_id, user_id)
        if not portfolio:
            return {"error": "Portfolio not found"}

        holdings_raw = portfolio.holdings if isinstance(portfolio.holdings, list) else ([portfolio.holdings] if portfolio.holdings else [])
        holdings_list = [
            {"ticker": h.ticker, "weight": h.weight, "quantity": h.quantity, "cost_basis": h.cost_basis}
            for h in holdings_raw
        ]

        mkt_prov = get_market_data_provider()
        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=365 * 2)

        price_series: Dict[str, List[float]] = {}
        for h in holdings_raw:
            bars = await mkt_prov.fetch_historical_bars(h.ticker, start_date, end_date)
            price_series[h.ticker] = [b.close for b in bars]

        metrics = self.engine.compute_portfolio_metrics(holdings_list, price_series)
        return {
            "portfolio_id": portfolio.id,
            "portfolio_name": portfolio.name,
            "user_id": portfolio.user_id,
            "holdings_count": len(holdings_raw),
            "metrics": metrics,
        }
