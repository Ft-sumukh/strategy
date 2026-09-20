"""
AEGIS INVEST — Portfolio Optimization Domain Service
Solves for optimal asset allocation weights under Markowitz, Minimum Variance,
Risk Parity, and Maximum Diversification objectives.
"""

from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.analytics.optimization.engine import PortfolioOptimizationEngine
from app.models.optimization import OptimizationRunRecord
from app.services.market_provider import get_market_data_provider
from app.services.portfolio_service import PortfolioService


class OptimizationService:
    """Domain service for mathematical portfolio optimization."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.engine = PortfolioOptimizationEngine()
        self.portfolio_service = PortfolioService(session)

    async def optimize_portfolio(
        self,
        portfolio_id: str,
        objective: str = "MAX_SHARPE",
        min_weight: float = 0.02,
        max_weight: float = 0.35,
        user_id: str = "default_user",
    ) -> Dict[str, Any]:
        portfolio = await self.portfolio_service.get_portfolio(portfolio_id, user_id)
        if not portfolio:
            return {"error": "Portfolio not found"}

        universe = [h.ticker for h in portfolio.holdings]
        curr_weights = {h.ticker: h.weight for h in portfolio.holdings}

        mkt_prov = get_market_data_provider()
        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=365 * 2)

        asset_returns: Dict[str, List[float]] = {}
        for t in universe:
            bars = await mkt_prov.fetch_historical_bars(t, start_date, end_date)
            if len(bars) >= 2:
                rets = [(bars[i].close - bars[i - 1].close) / bars[i - 1].close for i in range(1, len(bars))]
                asset_returns[t] = rets

        opt_res = self.engine.optimize_portfolio(
            universe=universe,
            asset_returns=asset_returns,
            objective=objective,
            min_weight=min_weight,
            max_weight=max_weight,
            current_weights=curr_weights,
        )

        # Save record
        rec = OptimizationRunRecord(
            portfolio_id=portfolio.id,
            objective=objective,
            universe=",".join(universe),
            constraints={"min_weight": min_weight, "max_weight": max_weight},
            initial_weights=curr_weights,
            optimized_weights=opt_res.get("optimized_weights", {}),
            weight_deltas=opt_res.get("weight_deltas", {}),
            expected_return=opt_res.get("expected_return", 0.0),
            expected_volatility=opt_res.get("expected_volatility", 0.0),
            expected_sharpe=opt_res.get("expected_sharpe", 0.0),
            diversification_ratio=opt_res.get("diversification_ratio", 1.0),
            solver_status=opt_res.get("status", "OPTIMAL"),
            notes=opt_res.get("notes"),
        )
        self.session.add(rec)
        await self.session.commit()

        return {
            "portfolio_id": portfolio.id,
            "portfolio_name": portfolio.name,
            "optimization_result": opt_res,
        }
