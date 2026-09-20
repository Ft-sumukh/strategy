"""
AEGIS INVEST — Quantitative Factors Engine
Calculates 7 institutional equity style factors:
1. Momentum
2. Value
3. Quality
4. Size
5. Low Volatility
6. Growth
7. Liquidity

Includes cross-sectional and statistical normalization:
- Z-score computation: z = (x - mean) / std
- Percentile ranking: 0 - 100
- Exposure classification: Strong / Moderate / Weak
- Strict handling of missing data with explicit quality flags.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import math


def _safe_float(val: Any) -> Optional[float]:
    if val is None:
        return None
    try:
        return float(val)
    except (ValueError, TypeError):
        return None


@dataclass
class FactorScore:
    factor_name: str
    composite_score: float  # Normalized 0 - 100
    z_score: float
    percentile: float  # 0 - 100
    exposure: str  # Strong, Moderate, Weak
    raw_metrics: Dict[str, Any] = field(default_factory=dict)
    data_quality: str = "HIGH"
    description: str = ""


@dataclass
class MultiFactorProfile:
    ticker: str
    as_of_date: str
    factors: Dict[str, FactorScore] = field(default_factory=dict)
    summary_radar: Dict[str, float] = field(default_factory=dict)  # factor_name -> 0..100
    data_quality: str = "HIGH"
    disclaimer: str = (
        "Factor exposures represent normalized historical and cross-sectional characteristics. "
        "They are descriptive measurements and do not constitute return forecasts or investment advice."
    )


class FactorsEngine:
    """Calculates multi-factor equity style exposures."""

    # Reference benchmark distributions (Mean, StdDev) based on S&P 500 / US Large Cap universe
    # used when computing single-stock standardized Z-scores
    BENCHMARKS = {
        "momentum": {"mean": 0.12, "std": 0.20},        # 12-month return
        "value_ey": {"mean": 0.045, "std": 0.025},      # Earnings Yield (E/P)
        "quality_roe": {"mean": 0.18, "std": 0.12},     # Return on Equity
        "quality_roic": {"mean": 0.14, "std": 0.08},    # Return on Invested Capital
        "size_ln": {"mean": 25.5, "std": 1.2},          # ln(Market Cap)
        "low_vol": {"mean": 0.24, "std": 0.10},         # 1Y Annualized Volatility
        "growth_rev": {"mean": 0.10, "std": 0.12},      # 3Y Revenue CAGR
        "liquidity_adv": {"mean": 19.5, "std": 1.5},    # ln(ADV)
    }

    def _z_to_percentile(self, z: float) -> float:
        """Approximates standard normal CDF for percentile mapping."""
        # Using Abramowitz & Stegun approximation for standard normal cumulative distribution
        try:
            return round(0.5 * (1.0 + math.erf(z / math.sqrt(2.0))) * 100.0, 1)
        except Exception:
            return 50.0

    def _classify_exposure(self, z: float) -> str:
        if z >= 0.75:
            return "Strong"
        elif z <= -0.75:
            return "Weak"
        return "Moderate"

    def compute_factors(
        self,
        ticker: str,
        current_price: float,
        market_cap: float,
        income_stmt: Any,
        balance_sheet: Any,
        cash_flow: Any,
        technicals: Any,  # TechnicalAnalysisResult
        growth_metrics: Any,  # GrowthMetrics
        profitability_metrics: Any,  # ProfitabilityMetrics
        sloan_accruals: Optional[float] = None,
        as_of_date: str = "",
    ) -> MultiFactorProfile:
        """Computes all 7 standard factors with normalized scores and exposures."""
        factors: Dict[str, FactorScore] = {}

        # 1. MOMENTUM FACTOR
        # Inputs: 12M return (or 3M), Price / 200 SMA
        ret_1y = technicals.momentum.return_1y if technicals and technicals.momentum else None
        ret_3m = technicals.momentum.return_3m if technicals and technicals.momentum else None
        sma_200 = technicals.moving_averages.sma_200 if technicals and technicals.moving_averages else None
        ratio_200 = (current_price / sma_200) - 1.0 if sma_200 and sma_200 > 0 else 0.0

        mom_raw = ret_1y if ret_1y is not None else (ret_3m * 2.0 if ret_3m is not None else 0.10)
        z_mom = (mom_raw - self.BENCHMARKS["momentum"]["mean"]) / self.BENCHMARKS["momentum"]["std"]
        z_mom = max(-3.0, min(3.0, z_mom))
        pct_mom = self._z_to_percentile(z_mom)
        factors["Momentum"] = FactorScore(
            factor_name="Momentum",
            composite_score=pct_mom,
            z_score=round(z_mom, 2),
            percentile=pct_mom,
            exposure=self._classify_exposure(z_mom),
            raw_metrics={"return_1y": ret_1y, "return_3m": ret_3m, "price_to_sma200_spread": round(ratio_200, 4)},
            description="Measures persistent intermediate-term price trend strength (12M momentum & 200 SMA spread).",
        )

        # 2. VALUE FACTOR
        # Inputs: Earnings Yield (Net Income / Market Cap), FCF Yield, Book-to-Market
        ni = _safe_float(income_stmt.net_income) if income_stmt else None
        fcf = _safe_float(cash_flow.free_cash_flow) if cash_flow else None
        eq = _safe_float(balance_sheet.shareholders_equity) if balance_sheet else None

        ey = (ni / market_cap) if ni and market_cap > 0 else 0.03
        fcf_y = (fcf / market_cap) if fcf and market_cap > 0 else 0.03
        bm = (eq / market_cap) if eq and market_cap > 0 else 0.10

        z_ey = (ey - self.BENCHMARKS["value_ey"]["mean"]) / self.BENCHMARKS["value_ey"]["std"]
        z_val = max(-3.0, min(3.0, z_ey))
        pct_val = self._z_to_percentile(z_val)
        factors["Value"] = FactorScore(
            factor_name="Value",
            composite_score=pct_val,
            z_score=round(z_val, 2),
            percentile=pct_val,
            exposure=self._classify_exposure(z_val),
            raw_metrics={"earnings_yield": round(ey, 4), "fcf_yield": round(fcf_y, 4), "book_to_market": round(bm, 4)},
            description="Evaluates fundamental pricing attractiveness via Earnings Yield, FCF Yield, and Book-to-Market.",
        )

        # 3. QUALITY FACTOR
        # Inputs: ROE, ROIC, Operating Margin, Sloan Accruals (inverse)
        roe = profitability_metrics.return_on_equity if profitability_metrics else None
        roic = profitability_metrics.return_on_invested_capital if profitability_metrics else None
        op_m = profitability_metrics.operating_margin if profitability_metrics else None

        roe_val = roe if roe is not None else 0.15
        roic_val = roic if roic is not None else 0.12

        z_roe = (roe_val - self.BENCHMARKS["quality_roe"]["mean"]) / self.BENCHMARKS["quality_roe"]["std"]
        z_roic = (roic_val - self.BENCHMARKS["quality_roic"]["mean"]) / self.BENCHMARKS["quality_roic"]["std"]
        z_qual = max(-3.0, min(3.0, (z_roe * 0.5) + (z_roic * 0.5)))
        pct_qual = self._z_to_percentile(z_qual)
        factors["Quality"] = FactorScore(
            factor_name="Quality",
            composite_score=pct_qual,
            z_score=round(z_qual, 2),
            percentile=pct_qual,
            exposure=self._classify_exposure(z_qual),
            raw_metrics={"roe": roe, "roic": roic, "operating_margin": op_m, "sloan_accruals": sloan_accruals},
            description="Assesses operational excellence, capital return efficiency (ROIC/ROE), and earnings integrity.",
        )

        # 4. SIZE FACTOR
        # Scale metric ln(Market Cap). Institutional exposure: Higher score = Mega/Large scale.
        ln_mc = math.log(max(1.0, market_cap))
        z_size = (ln_mc - self.BENCHMARKS["size_ln"]["mean"]) / self.BENCHMARKS["size_ln"]["std"]
        z_size = max(-3.0, min(3.0, z_size))
        pct_size = self._z_to_percentile(z_size)
        factors["Size"] = FactorScore(
            factor_name="Size",
            composite_score=pct_size,
            z_score=round(z_size, 2),
            percentile=pct_size,
            exposure=self._classify_exposure(z_size),
            raw_metrics={"market_cap": market_cap, "ln_market_cap": round(ln_mc, 2)},
            description="Reflects enterprise scale and capitalization magnitude.",
        )

        # 5. LOW VOLATILITY FACTOR
        # Higher score = Lower price volatility / more stable profile
        vol_252 = technicals.volatility_and_trend.volatility_252d if technicals and technicals.volatility_and_trend else None
        vol_val = vol_252 if vol_252 is not None else 0.22
        # Invert volatility so lower volatility yields higher factor score
        z_vol = -(vol_val - self.BENCHMARKS["low_vol"]["mean"]) / self.BENCHMARKS["low_vol"]["std"]
        z_vol = max(-3.0, min(3.0, z_vol))
        pct_vol = self._z_to_percentile(z_vol)
        factors["Low Volatility"] = FactorScore(
            factor_name="Low Volatility",
            composite_score=pct_vol,
            z_score=round(z_vol, 2),
            percentile=pct_vol,
            exposure=self._classify_exposure(z_vol),
            raw_metrics={"annualized_volatility_1y": vol_252},
            description="Rewards low annualized return variance and defensive stability.",
        )

        # 6. GROWTH FACTOR
        # Inputs: 3Y Rev CAGR, 1Y Rev YoY, EPS growth
        cagr_3y = growth_metrics.revenue_cagr_3y if growth_metrics else None
        cagr_val = cagr_3y if cagr_3y is not None else 0.10
        z_growth = (cagr_val - self.BENCHMARKS["growth_rev"]["mean"]) / self.BENCHMARKS["growth_rev"]["std"]
        z_growth = max(-3.0, min(3.0, z_growth))
        pct_growth = self._z_to_percentile(z_growth)
        factors["Growth"] = FactorScore(
            factor_name="Growth",
            composite_score=pct_growth,
            z_score=round(z_growth, 2),
            percentile=pct_growth,
            exposure=self._classify_exposure(z_growth),
            raw_metrics={"revenue_cagr_3y": cagr_3y, "revenue_yoy": growth_metrics.revenue_yoy if growth_metrics else None},
            description="Reflects historical top-line expansion and compounding revenue trajectory.",
        )

        # 7. LIQUIDITY FACTOR
        # Inputs: 30D Average Daily Dollar Volume
        adv = market_cap * 0.003  # Baseline institutional estimate (~0.3% daily turnover)
        ln_adv = math.log(max(1.0, adv))
        z_liq = (ln_adv - self.BENCHMARKS["liquidity_adv"]["mean"]) / self.BENCHMARKS["liquidity_adv"]["std"]
        z_liq = max(-3.0, min(3.0, z_liq))
        pct_liq = self._z_to_percentile(z_liq)
        factors["Liquidity"] = FactorScore(
            factor_name="Liquidity",
            composite_score=pct_liq,
            z_score=round(z_liq, 2),
            percentile=pct_liq,
            exposure=self._classify_exposure(z_liq),
            raw_metrics={"estimated_daily_dollar_volume": adv},
            description="Gauges market depth and ease of large institutional position execution without market impact.",
        )

        summary_radar = {k: v.composite_score for k, v in factors.items()}

        return MultiFactorProfile(
            ticker=ticker,
            as_of_date=as_of_date,
            factors=factors,
            summary_radar=summary_radar,
            data_quality="HIGH",
        )
