"""
AEGIS INVEST — Stress Testing & Scenario Analysis Engine
Applies historical crisis templates (2008 GFC, 2020 COVID, 2022 Rates) and
hypothetical macro shocks to multi-asset portfolios with beta & factor sensitivities.
"""

from typing import Any, Dict, List, Optional


DEFAULT_STRESS_SCENARIOS = [
    {
        "scenario_key": "2008_GFC",
        "name": "2008 Global Financial Crisis",
        "category": "HISTORICAL",
        "description": "Severe systemic banking solvency collapse, broad market liquidation, credit freeze, and multi-year economic contraction.",
        "equity_market_shock": -0.38,
        "rate_shock_bps": -200.0,
        "vix_spike": 55.0,
        "sector_multipliers": {"Financials": 1.45, "Technology": 0.95, "Consumer Discretionary": 1.15, "Utilities": 0.65},
        "recovery_months": 24.0,
    },
    {
        "scenario_key": "2020_COVID_SHOCK",
        "name": "2020 COVID-19 Liquidity Shock",
        "category": "HISTORICAL",
        "description": "Rapid global economic lockdown and acute margin-call liquidation followed by aggressive fiscal and monetary liquidity injection.",
        "equity_market_shock": -0.34,
        "rate_shock_bps": -150.0,
        "vix_spike": 65.0,
        "sector_multipliers": {"Energy": 1.50, "Financials": 1.20, "Technology": 0.80, "Healthcare": 0.70},
        "recovery_months": 6.0,
    },
    {
        "scenario_key": "2022_RATE_SHOCK",
        "name": "2022 Rapid Inflation & Rate Shock",
        "category": "HISTORICAL",
        "description": "Aggressive central bank rate hiking cycle to combat 40-year high inflation, leading to severe multiple compression on long-duration equities.",
        "equity_market_shock": -0.19,
        "rate_shock_bps": 350.0,
        "vix_spike": 20.0,
        "sector_multipliers": {"Technology": 1.55, "Consumer Discretionary": 1.40, "Energy": -0.80, "Utilities": 0.90},
        "recovery_months": 14.0,
    },
    {
        "scenario_key": "MARKET_CRASH_20",
        "name": "Hypothetical -20% Flash Crash",
        "category": "HYPOTHETICAL",
        "description": "Sudden 20% rapid liquidation event triggered by geopolitical or structural liquidity shocks.",
        "equity_market_shock": -0.20,
        "rate_shock_bps": -50.0,
        "vix_spike": 28.0,
        "sector_multipliers": {"Technology": 1.10, "Financials": 1.15, "Consumer Staples": 0.60},
        "recovery_months": 8.0,
    },
    {
        "scenario_key": "OIL_ENERGY_SHOCK",
        "name": "Geopolitical Energy Supply Disruption (+60% Oil)",
        "category": "HYPOTHETICAL",
        "description": "Major global oil shipping bottleneck spiking WTI crude oil +60%, accelerating headline inflation.",
        "equity_market_shock": -0.12,
        "rate_shock_bps": 100.0,
        "vix_spike": 18.0,
        "sector_multipliers": {"Energy": -1.80, "Industrials": 1.30, "Consumer Discretionary": 1.40, "Technology": 1.05},
        "recovery_months": 10.0,
    },
]


class StressTestEngine:
    """Calculates scenario impact estimates for a multi-asset portfolio."""

    def list_scenarios(self) -> List[Dict[str, Any]]:
        return DEFAULT_STRESS_SCENARIOS

    def run_stress_scenario(
        self,
        scenario_key: str,
        holdings: List[Dict[str, Any]],  # ticker, weight
        asset_betas: Optional[Dict[str, float]] = None,
        sector_map: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        Estimates the return, drawdown, and individual position impacts under the selected scenario.
        """
        scenario = next((s for s in DEFAULT_STRESS_SCENARIOS if s["scenario_key"] == scenario_key), None)
        if not scenario:
            scenario = DEFAULT_STRESS_SCENARIOS[0]

        betas = asset_betas or {}
        sectors = sector_map or {}
        base_shock = scenario["equity_market_shock"]
        sec_mults = scenario.get("sector_multipliers", {})

        position_impacts: Dict[str, float] = {}
        sector_impacts: Dict[str, float] = {}
        total_estimated_return = 0.0

        for h in holdings:
            ticker = h.get("ticker", "UNKNOWN")
            weight = float(h.get("weight", 0.0))
            if weight <= 0:
                continue

            sec = sectors.get(ticker, "Other")
            beta = float(betas.get(ticker, 1.0))
            sec_mult = float(sec_mults.get(sec, 1.0))

            # Estimated asset price move = base market shock * asset beta * sector multiplier
            asset_est_return = base_shock * beta * sec_mult
            # Clip between -95% and +150%
            asset_est_return = max(-0.95, min(1.50, asset_est_return))

            position_impacts[ticker] = round(asset_est_return, 4)
            weighted_impact = weight * asset_est_return
            total_estimated_return += weighted_impact

            sector_impacts[sec] = round(sector_impacts.get(sec, 0.0) + weighted_impact, 4)

        estimated_dd = abs(min(0.0, total_estimated_return))
        vol_spike = scenario["vix_spike"]

        return {
            "scenario_key": scenario["scenario_key"],
            "scenario_name": scenario["name"],
            "category": scenario["category"],
            "description": scenario["description"],
            "estimated_portfolio_return": round(total_estimated_return, 4),
            "estimated_drawdown": round(estimated_dd, 4),
            "estimated_volatility_spike": round(vol_spike, 1),
            "position_impacts": position_impacts,
            "sector_impacts": sector_impacts,
            "recovery_estimate_months": scenario["recovery_months"],
            "rationale": f"Scenario '{scenario['name']}' applies a baseline equity market shock of {base_shock*100:.1f}% adjusted by asset beta and sector risk multipliers.",
        }
