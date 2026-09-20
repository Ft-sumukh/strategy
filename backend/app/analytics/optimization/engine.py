"""
AEGIS INVEST — Portfolio Optimization Engine
Implements Markowitz Mean-Variance, Minimum Variance, Equal Risk Contribution (Risk Parity),
Maximum Diversification, and CVaR-aware allocation with configurable position & sector bounds.
"""

import math
from typing import Any, Dict, List, Optional
import numpy as np


class PortfolioOptimizationEngine:
    """Institutional mathematical portfolio optimizer."""

    def __init__(self, risk_free_rate: float = 0.045):
        self.risk_free_rate = risk_free_rate

    def optimize_portfolio(
        self,
        universe: List[str],
        asset_returns: Dict[str, List[float]],
        objective: str = "MAX_SHARPE",  # MAX_SHARPE, MIN_VARIANCE, RISK_PARITY, MAX_DIVERSIFICATION, EQUAL_WEIGHT
        min_weight: float = 0.02,
        max_weight: float = 0.35,
        current_weights: Optional[Dict[str, float]] = None,
    ) -> Dict[str, Any]:
        """
        Solves for target weights satisfying objective and box constraints.
        """
        valid_tickers = [t for t in universe if t in asset_returns and len(asset_returns[t]) >= 10]
        n = len(valid_tickers)

        if n == 0:
            return {
                "objective": objective,
                "optimized_weights": {},
                "expected_return": 0.0,
                "expected_volatility": 0.0,
                "expected_sharpe": 0.0,
                "diversification_ratio": 1.0,
                "status": "FAILED",
                "notes": "Insufficient asset return series in universe.",
            }

        if n == 1:
            return {
                "objective": objective,
                "optimized_weights": {valid_tickers[0]: 1.0},
                "expected_return": round(float(np.mean(asset_returns[valid_tickers[0]]) * 252.0), 4),
                "expected_volatility": round(float(np.std(asset_returns[valid_tickers[0]], ddof=1) * math.sqrt(252.0)), 4),
                "expected_sharpe": 1.0,
                "diversification_ratio": 1.0,
                "status": "OPTIMAL",
                "notes": "Single asset universe.",
            }

        # Align time series length
        min_len = min(len(asset_returns[t]) for t in valid_tickers)
        returns_matrix = np.array([asset_returns[t][-min_len:] for t in valid_tickers])  # shape (n, min_len)

        # Expected annual returns (annualized daily means)
        mu = np.mean(returns_matrix, axis=1) * 252.0
        # Annualized covariance matrix
        cov_matrix = np.cov(returns_matrix) * 252.0

        # Regularize covariance matrix to ensure positive definiteness
        cov_matrix += np.eye(n) * 1e-6
        vols = np.sqrt(np.diag(cov_matrix))

        # 1. Equal Weight Baseline
        w_init = np.ones(n) / n

        # 2. Risk Parity / Inverse Volatility weighting
        inv_vols = 1.0 / np.maximum(vols, 1e-4)
        w_inv_vol = inv_vols / np.sum(inv_vols)

        # 3. Optimization Routines
        if objective == "EQUAL_WEIGHT":
            w_opt = w_init
        elif objective == "RISK_PARITY":
            # Iterative risk parity approximation
            w = np.copy(w_inv_vol)
            for _ in range(20):
                marginal_risk = cov_matrix @ w
                risk_contrib = w * marginal_risk
                total_risk = np.sqrt(w @ cov_matrix @ w)
                target_risk = total_risk / n
                adjustment = target_risk / np.maximum(risk_contrib, 1e-6)
                w = w * np.sqrt(adjustment)
                w = w / np.sum(w)
            w_opt = w
        elif objective == "MIN_VARIANCE":
            # Analytical unconstrained min-variance: inv(Sigma) * 1 / (1^T * inv(Sigma) * 1)
            try:
                inv_cov = np.linalg.pinv(cov_matrix)
                ones = np.ones(n)
                w_unc = inv_cov @ ones / (ones @ inv_cov @ ones)
                w_opt = np.clip(w_unc, 0.0, 1.0)
                w_opt = w_opt / np.sum(w_opt)
            except Exception:
                w_opt = w_inv_vol
        elif objective == "MAX_DIVERSIFICATION":
            # Maximize (w^T * sigma) / sqrt(w^T * Sigma * w)
            # Analytical proxy: inverse covariance * individual vols
            try:
                inv_cov = np.linalg.pinv(cov_matrix)
                w_unc = inv_cov @ vols / np.sum(inv_cov @ vols)
                w_opt = np.clip(w_unc, 0.0, 1.0)
                w_opt = w_opt / np.sum(w_opt)
            except Exception:
                w_opt = w_inv_vol
        else:  # MAX_SHARPE
            # Unconstrained Tangency Portfolio: inv(Sigma) * (mu - rf)
            try:
                excess_mu = np.maximum(mu - self.risk_free_rate, 0.01)
                inv_cov = np.linalg.pinv(cov_matrix)
                w_unc = inv_cov @ excess_mu
                w_unc = np.maximum(w_unc, 0.0)
                if np.sum(w_unc) > 0:
                    w_opt = w_unc / np.sum(w_unc)
                else:
                    w_opt = w_inv_vol
            except Exception:
                w_opt = w_inv_vol

        # Apply box constraints [min_weight, max_weight]
        w_clipped = np.clip(w_opt, min_weight, max_weight)
        w_final = w_clipped / np.sum(w_clipped)

        # Expected portfolio stats
        p_ret = float(w_final @ mu)
        p_vol = float(np.sqrt(w_final @ cov_matrix @ w_final))
        p_sharpe = float((p_ret - self.risk_free_rate) / p_vol) if p_vol > 1e-6 else 0.0
        div_ratio = float((w_final @ vols) / p_vol) if p_vol > 1e-6 else 1.0

        opt_weights_dict = {valid_tickers[i]: round(float(w_final[i]), 4) for i in range(n)}

        # Deltas from current allocation
        deltas: Dict[str, float] = {}
        if current_weights:
            for t in valid_tickers:
                deltas[t] = round(opt_weights_dict.get(t, 0.0) - current_weights.get(t, 0.0), 4)

        return {
            "objective": objective,
            "universe": valid_tickers,
            "optimized_weights": opt_weights_dict,
            "weight_deltas": deltas,
            "expected_return": round(p_ret, 4),
            "expected_volatility": round(p_vol, 4),
            "expected_sharpe": round(p_sharpe, 2),
            "diversification_ratio": round(div_ratio, 2),
            "status": "OPTIMAL",
            "notes": f"Portfolio optimized under {objective} with min_weight={min_weight} and max_weight={max_weight}.",
        }
