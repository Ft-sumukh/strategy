"""
AEGIS INVEST — Portfolio Analytics Engine
Computes multi-asset portfolio performance, cumulative return curves,
HHI concentration, sector breakdowns, and liquidity scores.
"""

from datetime import datetime
import math
from typing import Any, Dict, List, Optional
import numpy as np


class PortfolioAnalyticsEngine:
    """Institutional calculation engine for multi-asset portfolios."""

    def __init__(self, risk_free_rate: float = 0.045):
        self.risk_free_rate = risk_free_rate

    def compute_portfolio_metrics(
        self,
        holdings: List[Dict[str, Any]],
        price_series: Dict[str, List[float]],
        sector_map: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        Computes comprehensive performance, allocation, and concentration metrics.
        
        holdings: list of dicts with keys: 'ticker', 'weight', 'cost_basis', 'quantity'
        price_series: dict mapping ticker -> list of historical close prices (ordered oldest to newest)
        """
        if not holdings:
            return {
                "total_return": 0.0,
                "annualized_return": 0.0,
                "annualized_volatility": 0.0,
                "sharpe_ratio": 0.0,
                "sortino_ratio": 0.0,
                "max_drawdown": 0.0,
                "hhi_concentration": 0.0,
                "sector_allocation": {},
                "weights": {},
                "daily_returns": [],
                "cumulative_returns": [],
            }

        # 1. Normalize weights
        raw_weights = {h["ticker"]: float(h.get("weight", 0.0)) for h in holdings}
        total_w = sum(raw_weights.values())
        if total_w <= 0:
            weights = {k: 1.0 / len(raw_weights) for k in raw_weights}
        else:
            weights = {k: v / total_w for k, v in raw_weights.items()}

        # 2. Herfindahl-Hirschman Index (HHI) concentration
        # HHI = sum(w_i^2), bounds in [1/N, 1.0]. Lower is more diversified.
        hhi = sum(w ** 2 for w in weights.values())

        # 3. Sector Allocation
        sectors = sector_map or {}
        sector_alloc: Dict[str, float] = {}
        for ticker, w in weights.items():
            sec = sectors.get(ticker, "Other")
            sector_alloc[sec] = round(sector_alloc.get(sec, 0.0) + w, 4)

        # 4. Synthesize daily portfolio returns from asset returns
        asset_returns: Dict[str, List[float]] = {}
        min_len = 999999
        for ticker, prices in price_series.items():
            if ticker not in weights:
                continue
            if len(prices) >= 2:
                rets = [
                    (prices[i] - prices[i - 1]) / prices[i - 1]
                    for i in range(1, len(prices))
                    if prices[i - 1] > 0
                ]
                asset_returns[ticker] = rets
                min_len = min(min_len, len(rets))

        if min_len == 999999 or min_len == 0 or not asset_returns:
            # Insufficient return series: fallback to static cost basis returns
            return {
                "total_return": 0.0,
                "annualized_return": 0.0,
                "annualized_volatility": 0.0,
                "sharpe_ratio": 0.0,
                "sortino_ratio": 0.0,
                "max_drawdown": 0.0,
                "hhi_concentration": round(hhi, 4),
                "sector_allocation": sector_alloc,
                "weights": {k: round(v, 4) for k, v in weights.items()},
                "daily_returns": [],
                "cumulative_returns": [1.0],
            }

        # Truncate all return arrays to common length
        aligned_returns = {t: rets[-min_len:] for t, rets in asset_returns.items()}
        daily_portfolio_returns = []
        for i in range(min_len):
            day_ret = sum(
                weights.get(t, 0.0) * aligned_returns[t][i]
                for t in aligned_returns
            )
            daily_portfolio_returns.append(day_ret)

        returns_arr = np.array(daily_portfolio_returns)
        n_days = len(returns_arr)

        # Cumulative return curve
        cum_curve = [1.0]
        for r in daily_portfolio_returns:
            cum_curve.append(cum_curve[-1] * (1.0 + r))

        total_return = float(cum_curve[-1] - 1.0)
        years = max(n_days / 252.0, 1.0 / 252.0)
        annualized_return = float((1.0 + total_return) ** (1.0 / years) - 1.0) if total_return > -1.0 else -1.0

        # Realized Volatility
        daily_vol = float(np.std(returns_arr, ddof=1)) if len(returns_arr) > 1 else 0.0
        annualized_vol = daily_vol * math.sqrt(252.0)

        # Sharpe Ratio
        excess_return = annualized_return - self.risk_free_rate
        sharpe = excess_return / annualized_vol if annualized_vol > 1e-6 else 0.0

        # Downside deviation & Sortino Ratio
        downside_returns = returns_arr[returns_arr < 0]
        if len(downside_returns) > 1:
            downside_std = float(np.sqrt(np.mean(downside_returns ** 2))) * math.sqrt(252.0)
            sortino = excess_return / downside_std if downside_std > 1e-6 else 0.0
        else:
            sortino = sharpe

        # Maximum Drawdown
        peak = cum_curve[0]
        max_dd = 0.0
        for val in cum_curve:
            if val > peak:
                peak = val
            dd = (peak - val) / peak if peak > 0 else 0.0
            if dd > max_dd:
                max_dd = dd

        return {
            "total_return": round(total_return, 4),
            "annualized_return": round(annualized_return, 4),
            "annualized_volatility": round(annualized_vol, 4),
            "sharpe_ratio": round(sharpe, 2),
            "sortino_ratio": round(sortino, 2),
            "max_drawdown": round(max_dd, 4),
            "hhi_concentration": round(hhi, 4),
            "sector_allocation": sector_alloc,
            "weights": {k: round(v, 4) for k, v in weights.items()},
            "daily_returns": [round(float(r), 6) for r in daily_portfolio_returns[-60:]],
            "cumulative_returns": [round(float(c), 4) for c in cum_curve[-60:]],
        }
