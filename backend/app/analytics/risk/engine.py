"""
AEGIS INVEST — Risk Analytics Engine
Computes institutional risk decomposition: VaR 95/99, CVaR (Expected Shortfall),
asset correlation matrices, multi-factor risk exposures, and portfolio drawdown statistics.
"""

import math
from typing import Any, Dict, List, Optional
import numpy as np


class RiskEngine:
    """Comprehensive quantitative risk and scenario analysis engine."""

    def __init__(self, risk_free_rate: float = 0.045):
        self.risk_free_rate = risk_free_rate

    def compute_risk_profile(
        self,
        returns: List[float],
        benchmark_returns: Optional[List[float]] = None,
        asset_returns_map: Optional[Dict[str, List[float]]] = None,
        weights_map: Optional[Dict[str, float]] = None,
    ) -> Dict[str, Any]:
        """
        Computes VaR, CVaR, Beta, Downside Deviation, and Asset Correlations.
        
        returns: List of daily portfolio returns.
        benchmark_returns: List of daily benchmark returns (e.g. SPY proxy).
        asset_returns_map: Dict of ticker -> daily returns.
        weights_map: Dict of ticker -> weight fraction.
        """
        if not returns or len(returns) < 5:
            return {
                "annualized_volatility": 0.0,
                "downside_deviation": 0.0,
                "var_95": 0.0,
                "var_99": 0.0,
                "cvar_95": 0.0,
                "beta": 1.0,
                "correlation_matrix": {},
                "factor_exposures": {
                    "Market": 1.0, "Size": 0.0, "Value": 0.0,
                    "Momentum": 0.0, "Quality": 0.0, "LowVol": 0.0
                },
            }

        ret_arr = np.array(returns, dtype=float)
        n = len(ret_arr)

        # 1. Realized Volatility
        daily_vol = float(np.std(ret_arr, ddof=1))
        annualized_vol = daily_vol * math.sqrt(252.0)

        # 2. Downside Deviation
        neg_rets = ret_arr[ret_arr < 0]
        downside_dev = (
            float(np.sqrt(np.mean(neg_rets ** 2))) * math.sqrt(252.0)
            if len(neg_rets) > 0
            else 0.0
        )

        # 3. Value at Risk (Historical Percentile Approach)
        # 1-day 95% and 99% VaR expressed as positive percentage loss
        sorted_rets = np.sort(ret_arr)
        idx_95 = max(0, int(0.05 * n))
        idx_99 = max(0, int(0.01 * n))
        var_95 = float(-sorted_rets[idx_95]) if sorted_rets[idx_95] < 0 else 0.0
        var_99 = float(-sorted_rets[idx_99]) if sorted_rets[idx_99] < 0 else 0.0

        # 4. Conditional VaR (Expected Shortfall at 95%)
        # Average loss beyond the 95% VaR threshold
        tail_95 = sorted_rets[:idx_95 + 1]
        cvar_95 = float(-np.mean(tail_95)) if len(tail_95) > 0 and np.mean(tail_95) < 0 else var_95

        # 5. Beta against Benchmark
        beta = 1.0
        if benchmark_returns and len(benchmark_returns) >= 5:
            min_l = min(len(ret_arr), len(benchmark_returns))
            p_slice = ret_arr[-min_l:]
            b_slice = np.array(benchmark_returns[-min_l:], dtype=float)
            b_var = float(np.var(b_slice, ddof=1))
            if b_var > 1e-8:
                cov = float(np.cov(p_slice, b_slice)[0][1])
                beta = cov / b_var

        # 6. Asset Correlation Matrix
        corr_matrix: Dict[str, Dict[str, float]] = {}
        if asset_returns_map and len(asset_returns_map) > 1:
            tickers = sorted(asset_returns_map.keys())
            # Find min length across assets
            min_len_assets = min(len(asset_returns_map[t]) for t in tickers if len(asset_returns_map[t]) > 0)
            if min_len_assets >= 5:
                series_matrix = np.array([
                    asset_returns_map[t][-min_len_assets:] for t in tickers
                ])
                raw_corr = np.corrcoef(series_matrix)
                for i, t1 in enumerate(tickers):
                    corr_matrix[t1] = {}
                    for j, t2 in enumerate(tickers):
                        val = float(raw_corr[i, j])
                        corr_matrix[t1][t2] = 1.0 if i == j else (0.0 if np.isnan(val) else round(val, 3))

        # 7. Factor Exposure Estimation (Fama-French Proxy)
        # Market, Size (SMB), Value (HML), Momentum (UMD), Quality (QMJ), Low Vol (BAB)
        # Approximated from portfolio characteristics and asset beta
        factor_exposures = {
            "Market": round(beta, 2),
            "Size": round(float(np.clip(1.2 - beta * 0.5, -0.5, 0.8)), 2),
            "Value": round(float(np.clip(0.4 - annualized_vol * 1.2, -0.6, 0.6)), 2),
            "Momentum": round(float(np.clip(np.mean(ret_arr) * 252.0 * 2.0, -0.8, 1.2)), 2),
            "Quality": round(float(np.clip(0.8 - downside_dev * 1.5, -0.3, 0.9)), 2),
            "LowVol": round(float(np.clip(1.0 - annualized_vol * 3.0, -0.9, 0.9)), 2),
        }

        return {
            "annualized_volatility": round(annualized_vol, 4),
            "downside_deviation": round(downside_dev, 4),
            "var_95": round(var_95, 4),
            "var_99": round(var_99, 4),
            "cvar_95": round(cvar_95, 4),
            "beta": round(beta, 2),
            "correlation_matrix": corr_matrix,
            "factor_exposures": factor_exposures,
        }
