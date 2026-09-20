"""
AEGIS INVEST — Risk Domain Service
Computes portfolio and universe risk metrics, historical VaR / CVaR,
correlation matrices, and multi-factor risk exposures.
"""

from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.analytics.risk.engine import RiskEngine
from app.services.market_provider import get_market_data_provider
from app.services.portfolio_service import PortfolioService


class RiskService:
    """Domain service for risk analysis."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.engine = RiskEngine()
        self.portfolio_service = PortfolioService(session)

    async def get_portfolio_risk_profile(self, portfolio_id: str, user_id: str = "default_user") -> Dict[str, Any]:
        portfolio = await self.portfolio_service.get_portfolio(portfolio_id, user_id)
        if not portfolio:
            return {"error": "Portfolio not found"}

        mkt_prov = get_market_data_provider()
        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=365 * 2)

        asset_returns: Dict[str, List[float]] = {}
        for h in portfolio.holdings:
            bars = await mkt_prov.fetch_historical_bars(h.ticker, start_date, end_date)
            if len(bars) >= 2:
                rets = [(bars[i].close - bars[i - 1].close) / bars[i - 1].close for i in range(1, len(bars))]
                asset_returns[h.ticker] = rets

        # SPY Benchmark returns
        spy_bars = await mkt_prov.fetch_historical_bars("SPY", start_date, end_date)
        if not spy_bars and portfolio.holdings:
            # Fallback benchmark to first holding
            spy_bars = await mkt_prov.fetch_historical_bars(portfolio.holdings[0].ticker, start_date, end_date)

        bm_returns = [(spy_bars[i].close - spy_bars[i - 1].close) / spy_bars[i - 1].close for i in range(1, len(spy_bars))] if len(spy_bars) >= 2 else []

        # Portfolio synthetic daily returns
        weights = {h.ticker: h.weight for h in portfolio.holdings}
        min_l = min(len(asset_returns[t]) for t in asset_returns) if asset_returns else 0
        portfolio_returns = []
        if min_l > 0:
            for i in range(min_l):
                r = sum(weights.get(t, 0.0) * asset_returns[t][-min_l + i] for t in asset_returns)
                portfolio_returns.append(r)

        risk_metrics = self.engine.compute_risk_profile(
            returns=portfolio_returns,
            benchmark_returns=bm_returns,
            asset_returns_map=asset_returns,
            weights_map=weights,
        )

        return {
            "portfolio_id": portfolio.id,
            "portfolio_name": portfolio.name,
            "user_id": portfolio.user_id,
            "holdings_count": len(portfolio.holdings),
            "risk_metrics": risk_metrics,
        }
