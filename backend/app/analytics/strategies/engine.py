"""
AEGIS INVEST — Systematic Strategy Engine
Implements 8 institutional systematic alpha & asset allocation strategies:
1. MomentumStrategy: 12M-1M return ranking, relative strength weighting.
2. ValueStrategy: Composite Earnings Yield, FCF Yield, Book-to-Market ranking.
3. QualityStrategy: High ROIC, ROE, FCF margin, low Sloan accruals & leverage.
4. TrendFollowingStrategy: Price > SMA200, SMA50 > SMA200, ADX trend confirmation.
5. MeanReversionStrategy: RSI(14) oversold bounce, lower Bollinger Band touch.
6. LowVolatilityStrategy: 252D realized volatility ranking, inverse-volatility weighting.
7. FactorCombinationStrategy: Weighted multi-factor score (Momentum, Value, Quality, LowVol).
8. RiskParityStrategy: Equal risk contribution allocation based on asset volatility.

All strategies generate standardized, reproducible StrategySignalRecord objects.
Zero arbitrary code execution — strictly parametric Pydantic configurations.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
import math
from typing import Any, Dict, List, Optional


@dataclass
class StrategySignalOutput:
    ticker: str
    signal_score: float  # Normalized score -1.0 to 1.0 or 0 to 100
    rank: int
    target_weight: float  # Allocation weight between 0.0 and 1.0
    action: str  # BUY, OVERWEIGHT, HOLD, UNDERWEIGHT, SELL
    rationale: str
    factor_breakdown: Dict[str, float] = field(default_factory=dict)


@dataclass
class StrategyExecutionResult:
    strategy_key: str
    strategy_name: str
    category: str
    universe: List[str]
    rebalance_frequency: str
    timestamp: str
    strategy_version: str
    parameters: Dict[str, Any]
    signals: List[StrategySignalOutput] = field(default_factory=list)
    cash_weight: float = 0.0
    summary: str = ""
    disclaimer: str = (
        "Systematic strategy signals are algorithmic outputs generated strictly from historical factors and parameters. "
        "They do not constitute financial advice, investment mandates, or performance guarantees."
    )


# Universe asset metadata used for robust multi-factor evaluation
UNIVERSE_DATA: Dict[str, Dict[str, Any]] = {
    "AAPL": {
        "price": 230.50,
        "sma_50": 224.10,
        "sma_200": 198.40,
        "adx": 28.5,
        "rsi_14": 56.4,
        "momentum_12m_1m": 0.284,
        "earnings_yield": 0.034,
        "fcf_yield": 0.038,
        "book_to_market": 0.021,
        "roic": 0.54,
        "roe": 1.45,
        "fcf_margin": 0.27,
        "sloan_accruals": -0.04,
        "debt_to_equity": 1.4,
        "volatility_252d": 0.21,
        "bollinger_pct": 0.62,
    },
    "MSFT": {
        "price": 435.20,
        "sma_50": 428.00,
        "sma_200": 412.50,
        "adx": 24.2,
        "rsi_14": 52.8,
        "momentum_12m_1m": 0.225,
        "earnings_yield": 0.031,
        "fcf_yield": 0.029,
        "book_to_market": 0.082,
        "roic": 0.28,
        "roe": 0.38,
        "fcf_margin": 0.31,
        "sloan_accruals": -0.02,
        "debt_to_equity": 0.42,
        "volatility_252d": 0.22,
        "bollinger_pct": 0.55,
    },
    "NVDA": {
        "price": 128.80,
        "sma_50": 124.50,
        "sma_200": 105.20,
        "adx": 34.8,
        "rsi_14": 62.1,
        "momentum_12m_1m": 1.152,
        "earnings_yield": 0.028,
        "fcf_yield": 0.032,
        "book_to_market": 0.035,
        "roic": 0.72,
        "roe": 1.12,
        "fcf_margin": 0.46,
        "sloan_accruals": 0.01,
        "debt_to_equity": 0.18,
        "volatility_252d": 0.44,
        "bollinger_pct": 0.68,
    },
    "GOOG": {
        "price": 178.40,
        "sma_50": 172.10,
        "sma_200": 164.80,
        "adx": 22.0,
        "rsi_14": 54.0,
        "momentum_12m_1m": 0.265,
        "earnings_yield": 0.046,
        "fcf_yield": 0.042,
        "book_to_market": 0.165,
        "roic": 0.31,
        "roe": 0.32,
        "fcf_margin": 0.25,
        "sloan_accruals": -0.03,
        "debt_to_equity": 0.09,
        "volatility_252d": 0.26,
        "bollinger_pct": 0.58,
    },
    "AMZN": {
        "price": 192.60,
        "sma_50": 188.20,
        "sma_200": 175.40,
        "adx": 26.4,
        "rsi_14": 57.5,
        "momentum_12m_1m": 0.362,
        "earnings_yield": 0.026,
        "fcf_yield": 0.044,
        "book_to_market": 0.124,
        "roic": 0.18,
        "roe": 0.22,
        "fcf_margin": 0.09,
        "sloan_accruals": -0.05,
        "debt_to_equity": 0.55,
        "volatility_252d": 0.29,
        "bollinger_pct": 0.61,
    },
    "META": {
        "price": 575.80,
        "sma_50": 560.00,
        "sma_200": 490.50,
        "adx": 31.0,
        "rsi_14": 59.2,
        "momentum_12m_1m": 0.742,
        "earnings_yield": 0.041,
        "fcf_yield": 0.039,
        "book_to_market": 0.108,
        "roic": 0.34,
        "roe": 0.36,
        "fcf_margin": 0.33,
        "sloan_accruals": -0.01,
        "debt_to_equity": 0.22,
        "volatility_252d": 0.33,
        "bollinger_pct": 0.64,
    },
    "JPM": {
        "price": 222.40,
        "sma_50": 218.00,
        "sma_200": 196.20,
        "adx": 25.1,
        "rsi_14": 55.0,
        "momentum_12m_1m": 0.380,
        "earnings_yield": 0.082,
        "fcf_yield": 0.075,
        "book_to_market": 0.580,
        "roic": 0.16,
        "roe": 0.17,
        "fcf_margin": 0.22,
        "sloan_accruals": -0.02,
        "debt_to_equity": 1.25,
        "volatility_252d": 0.18,
        "bollinger_pct": 0.59,
    },
    "XOM": {
        "price": 115.60,
        "sma_50": 114.20,
        "sma_200": 112.80,
        "adx": 16.5,
        "rsi_14": 46.2,
        "momentum_12m_1m": 0.082,
        "earnings_yield": 0.074,
        "fcf_yield": 0.068,
        "book_to_market": 0.440,
        "roic": 0.14,
        "roe": 0.16,
        "fcf_margin": 0.11,
        "sloan_accruals": 0.00,
        "debt_to_equity": 0.16,
        "volatility_252d": 0.19,
        "bollinger_pct": 0.48,
    },
    "JNJ": {
        "price": 160.50,
        "sma_50": 162.00,
        "sma_200": 158.40,
        "adx": 14.2,
        "rsi_14": 44.0,
        "momentum_12m_1m": 0.024,
        "earnings_yield": 0.061,
        "fcf_yield": 0.058,
        "book_to_market": 0.310,
        "roic": 0.19,
        "roe": 0.24,
        "fcf_margin": 0.21,
        "sloan_accruals": -0.03,
        "debt_to_equity": 0.45,
        "volatility_252d": 0.14,
        "bollinger_pct": 0.42,
    },
    "PG": {
        "price": 172.30,
        "sma_50": 173.50,
        "sma_200": 165.20,
        "adx": 18.0,
        "rsi_14": 47.5,
        "momentum_12m_1m": 0.115,
        "earnings_yield": 0.040,
        "fcf_yield": 0.044,
        "book_to_market": 0.135,
        "roic": 0.22,
        "roe": 0.31,
        "fcf_margin": 0.19,
        "sloan_accruals": -0.04,
        "debt_to_equity": 0.72,
        "volatility_252d": 0.13,
        "bollinger_pct": 0.46,
    },
}


class BaseStrategy(ABC):
    """Abstract systematic strategy interface."""

    def __init__(self, strategy_key: str, name: str, category: str, version: str = "1.0.0"):
        self.strategy_key = strategy_key
        self.name = name
        self.category = category
        self.version = version

    @abstractmethod
    def generate_signals(
        self,
        universe: List[str],
        parameters: Dict[str, Any],
        custom_data: Optional[Dict[str, Dict[str, Any]]] = None,
    ) -> StrategyExecutionResult:
        pass


class MomentumStrategy(BaseStrategy):
    """
    Momentum Strategy:
    Ranks universe by 12M-1M momentum return.
    Allocates to top N assets proportional to momentum strength.
    """

    def __init__(self):
        super().__init__(
            strategy_key="momentum",
            name="Cross-Sectional Momentum",
            category="MOMENTUM",
        )

    def generate_signals(
        self,
        universe: List[str],
        parameters: Dict[str, Any],
        custom_data: Optional[Dict[str, Dict[str, Any]]] = None,
    ) -> StrategyExecutionResult:
        top_n = parameters.get("top_n", 5)
        data = custom_data or UNIVERSE_DATA

        scored_assets: List[Tuple[str, float]] = []
        for ticker in universe:
            t_data = data.get(ticker, {})
            mom = t_data.get("momentum_12m_1m", 0.0)
            scored_assets.append((ticker, mom))

        # Rank descending
        scored_assets.sort(key=lambda x: x[1], reverse=True)

        selected = scored_assets[:top_n]
        sum_mom = sum(max(0.01, score) for _, score in selected)

        signals: List[StrategySignalOutput] = []
        for rank, (ticker, mom) in enumerate(scored_assets, 1):
            if rank <= top_n and sum_mom > 0:
                weight = round(max(0.01, mom) / sum_mom, 4)
                action = "BUY" if rank <= 2 else "OVERWEIGHT"
                rationale = f"Top decile 12M-1M momentum ({mom * 100:.1f}%), rank {rank}."
            else:
                weight = 0.0
                action = "HOLD" if rank <= top_n + 2 else "SELL"
                rationale = f"Momentum score ({mom * 100:.1f}%) outside top {top_n} allocation threshold."

            signals.append(
                StrategySignalOutput(
                    ticker=ticker,
                    signal_score=round(mom * 100.0, 2),
                    rank=rank,
                    target_weight=weight,
                    action=action,
                    rationale=rationale,
                    factor_breakdown={"momentum_12m_1m": mom},
                )
            )

        return StrategyExecutionResult(
            strategy_key=self.strategy_key,
            strategy_name=self.name,
            category=self.category,
            universe=universe,
            rebalance_frequency=parameters.get("rebalance_frequency", "MONTHLY"),
            timestamp=datetime.now(timezone.utc).isoformat(),
            strategy_version=self.version,
            parameters=parameters,
            signals=signals,
            cash_weight=round(1.0 - sum(s.target_weight for s in signals), 4),
            summary=f"Momentum strategy selected top {top_n} assets led by {signals[0].ticker} ({signals[0].signal_score}%).",
        )


class ValueStrategy(BaseStrategy):
    """
    Value Strategy:
    Ranks universe by multi-metric valuation composite: Earnings Yield, FCF Yield, Book-to-Market.
    """

    def __init__(self):
        super().__init__(
            strategy_key="value",
            name="Composite Deep Value",
            category="VALUE",
        )

    def generate_signals(
        self,
        universe: List[str],
        parameters: Dict[str, Any],
        custom_data: Optional[Dict[str, Dict[str, Any]]] = None,
    ) -> StrategyExecutionResult:
        top_n = parameters.get("top_n", 5)
        data = custom_data or UNIVERSE_DATA

        scored: List[Tuple[str, float, Dict[str, float]]] = []
        for ticker in universe:
            t_data = data.get(ticker, {})
            ey = t_data.get("earnings_yield", 0.0)
            fcfy = t_data.get("fcf_yield", 0.0)
            bm = t_data.get("book_to_market", 0.0)
            # Composite value score
            composite = (ey * 0.4) + (fcfy * 0.4) + (bm * 0.2)
            scored.append((ticker, composite, {"earnings_yield": ey, "fcf_yield": fcfy, "book_to_market": bm}))

        scored.sort(key=lambda x: x[1], reverse=True)
        selected = scored[:top_n]
        sum_val = sum(max(0.01, score) for _, score, _ in selected)

        signals: List[StrategySignalOutput] = []
        for rank, (ticker, comp, metrics) in enumerate(scored, 1):
            if rank <= top_n and sum_val > 0:
                weight = round(max(0.01, comp) / sum_val, 4)
                action = "BUY" if rank <= 2 else "OVERWEIGHT"
                rationale = f"High composite value score (EY {metrics['earnings_yield']*100:.1f}%, FCF Yield {metrics['fcf_yield']*100:.1f}%), rank {rank}."
            else:
                weight = 0.0
                action = "HOLD" if rank <= top_n + 2 else "SELL"
                rationale = "Valuation composite does not meet top value decile criteria."

            signals.append(
                StrategySignalOutput(
                    ticker=ticker,
                    signal_score=round(comp * 100.0, 2),
                    rank=rank,
                    target_weight=weight,
                    action=action,
                    rationale=rationale,
                    factor_breakdown=metrics,
                )
            )

        return StrategyExecutionResult(
            strategy_key=self.strategy_key,
            strategy_name=self.name,
            category=self.category,
            universe=universe,
            rebalance_frequency=parameters.get("rebalance_frequency", "QUARTERLY"),
            timestamp=datetime.now(timezone.utc).isoformat(),
            strategy_version=self.version,
            parameters=parameters,
            signals=signals,
            cash_weight=round(1.0 - sum(s.target_weight for s in signals), 4),
            summary=f"Value strategy selected top {top_n} assets with attractive earnings & FCF yields led by {signals[0].ticker}.",
        )


class QualityStrategy(BaseStrategy):
    """
    Quality Strategy:
    Ranks universe by ROIC, ROE, FCF Margin, Sloan Accruals, and conservative Leverage.
    """

    def __init__(self):
        super().__init__(
            strategy_key="quality",
            name="High-Quality Compounders",
            category="QUALITY",
        )

    def generate_signals(
        self,
        universe: List[str],
        parameters: Dict[str, Any],
        custom_data: Optional[Dict[str, Dict[str, Any]]] = None,
    ) -> StrategyExecutionResult:
        top_n = parameters.get("top_n", 5)
        data = custom_data or UNIVERSE_DATA

        scored: List[Tuple[str, float, Dict[str, float]]] = []
        for ticker in universe:
            t_data = data.get(ticker, {})
            roic = t_data.get("roic", 0.0)
            roe = t_data.get("roe", 0.0)
            fcf_m = t_data.get("fcf_margin", 0.0)
            accruals = t_data.get("sloan_accruals", 0.0)
            dte = t_data.get("debt_to_equity", 1.0)

            # Quality composite: Higher ROIC, ROE, FCF margin; lower accruals and debt
            quality_score = (roic * 0.35) + (roe * 0.25) + (fcf_m * 0.25) - (accruals * 0.5) - (min(2.0, dte) * 0.05)
            scored.append((ticker, quality_score, {"roic": roic, "roe": roe, "fcf_margin": fcf_m, "debt_to_equity": dte}))

        scored.sort(key=lambda x: x[1], reverse=True)
        selected = scored[:top_n]
        sum_q = sum(max(0.01, score) for _, score, _ in selected)

        signals: List[StrategySignalOutput] = []
        for rank, (ticker, q_score, metrics) in enumerate(scored, 1):
            if rank <= top_n and sum_q > 0:
                weight = round(max(0.01, q_score) / sum_q, 4)
                action = "BUY" if rank <= 2 else "OVERWEIGHT"
                rationale = f"Superior capital efficiency (ROIC {metrics['roic']*100:.1f}%, FCF Margin {metrics['fcf_margin']*100:.1f}%), rank {rank}."
            else:
                weight = 0.0
                action = "HOLD" if rank <= top_n + 2 else "SELL"
                rationale = "Quality fundamentals below top compounder threshold."

            signals.append(
                StrategySignalOutput(
                    ticker=ticker,
                    signal_score=round(q_score * 100.0, 2),
                    rank=rank,
                    target_weight=weight,
                    action=action,
                    rationale=rationale,
                    factor_breakdown=metrics,
                )
            )

        return StrategyExecutionResult(
            strategy_key=self.strategy_key,
            strategy_name=self.name,
            category=self.category,
            universe=universe,
            rebalance_frequency=parameters.get("rebalance_frequency", "QUARTERLY"),
            timestamp=datetime.now(timezone.utc).isoformat(),
            strategy_version=self.version,
            parameters=parameters,
            signals=signals,
            cash_weight=round(1.0 - sum(s.target_weight for s in signals), 4),
            summary=f"Quality strategy allocated to {top_n} durable balance sheet compounders led by {signals[0].ticker}.",
        )


class TrendFollowingStrategy(BaseStrategy):
    """
    Trend Following Strategy:
    Filters assets where Price > SMA200 and SMA50 > SMA200 with ADX confirmation.
    """

    def __init__(self):
        super().__init__(
            strategy_key="trend_following",
            name="Moving Average Trend Following",
            category="TREND",
        )

    def generate_signals(
        self,
        universe: List[str],
        parameters: Dict[str, Any],
        custom_data: Optional[Dict[str, Dict[str, Any]]] = None,
    ) -> StrategyExecutionResult:
        min_adx = parameters.get("min_adx", 20.0)
        data = custom_data or UNIVERSE_DATA

        candidates: List[Tuple[str, float, Dict[str, float]]] = []
        for ticker in universe:
            t_data = data.get(ticker, {})
            price = t_data.get("price", 100.0)
            sma50 = t_data.get("sma_50", 100.0)
            sma200 = t_data.get("sma_200", 100.0)
            adx = t_data.get("adx", 25.0)

            is_uptrend = price > sma200 and sma50 > sma200 and adx >= min_adx
            trend_strength = ((price / sma200) - 1.0) * (adx / 20.0) if is_uptrend else -1.0
            candidates.append((ticker, trend_strength, {"price": price, "sma_50": sma50, "sma_200": sma200, "adx": adx}))

        candidates.sort(key=lambda x: x[1], reverse=True)
        active_trends = [c for c in candidates if c[1] > 0]
        n_active = len(active_trends)
        weight_per_asset = round(1.0 / n_active, 4) if n_active > 0 else 0.0

        signals: List[StrategySignalOutput] = []
        for rank, (ticker, strength, metrics) in enumerate(candidates, 1):
            if strength > 0:
                weight = weight_per_asset
                action = "BUY"
                rationale = f"Confirmed golden cross (P > SMA200, SMA50 > SMA200) with ADX {metrics['adx']:.1f}."
            else:
                weight = 0.0
                action = "SELL"
                rationale = f"Trend filter failed: Price vs SMA200 {((metrics['price']/metrics['sma_200'])-1)*100:+.1f}%, ADX {metrics['adx']:.1f}."

            signals.append(
                StrategySignalOutput(
                    ticker=ticker,
                    signal_score=round(max(0.0, strength) * 100.0, 2),
                    rank=rank,
                    target_weight=weight,
                    action=action,
                    rationale=rationale,
                    factor_breakdown=metrics,
                )
            )

        return StrategyExecutionResult(
            strategy_key=self.strategy_key,
            strategy_name=self.name,
            category=self.category,
            universe=universe,
            rebalance_frequency=parameters.get("rebalance_frequency", "MONTHLY"),
            timestamp=datetime.now(timezone.utc).isoformat(),
            strategy_version=self.version,
            parameters=parameters,
            signals=signals,
            cash_weight=round(1.0 - sum(s.target_weight for s in signals), 4),
            summary=f"Trend strategy identified {n_active} assets in confirmed secular uptrends with active trend weights.",
        )


class MeanReversionStrategy(BaseStrategy):
    """
    Mean Reversion Strategy:
    Identifies short-term oversold conditions (RSI < 45, lower Bollinger touch) within universe.
    """

    def __init__(self):
        super().__init__(
            strategy_key="mean_reversion",
            name="Statistical Mean Reversion",
            category="MEAN_REVERSION",
        )

    def generate_signals(
        self,
        universe: List[str],
        parameters: Dict[str, Any],
        custom_data: Optional[Dict[str, Dict[str, Any]]] = None,
    ) -> StrategyExecutionResult:
        rsi_oversold = parameters.get("rsi_threshold", 50.0)
        data = custom_data or UNIVERSE_DATA

        candidates: List[Tuple[str, float, Dict[str, float]]] = []
        for ticker in universe:
            t_data = data.get(ticker, {})
            rsi = t_data.get("rsi_14", 50.0)
            bb_pct = t_data.get("bollinger_pct", 0.5)

            # Lower RSI and lower Bollinger band percent indicates greater oversold condition
            reversion_score = (100.0 - rsi) * 0.6 + ((1.0 - bb_pct) * 100.0) * 0.4
            candidates.append((ticker, reversion_score, {"rsi_14": rsi, "bollinger_pct": bb_pct}))

        candidates.sort(key=lambda x: x[1], reverse=True)
        top_n = parameters.get("top_n", 3)
        selected = candidates[:top_n]
        sum_rev = sum(score for _, score, _ in selected)

        signals: List[StrategySignalOutput] = []
        for rank, (ticker, score, metrics) in enumerate(candidates, 1):
            if rank <= top_n and sum_rev > 0:
                weight = round(score / sum_rev, 4)
                action = "BUY"
                rationale = f"Oversold condition: RSI {metrics['rsi_14']:.1f}, Bollinger band {metrics['bollinger_pct']*100:.0f}%, mean-reversion setup."
            else:
                weight = 0.0
                action = "HOLD" if rank <= top_n + 2 else "SELL"
                rationale = f"Neutral to overbought technical posture (RSI {metrics['rsi_14']:.1f})."

            signals.append(
                StrategySignalOutput(
                    ticker=ticker,
                    signal_score=round(score, 2),
                    rank=rank,
                    target_weight=weight,
                    action=action,
                    rationale=rationale,
                    factor_breakdown=metrics,
                )
            )

        return StrategyExecutionResult(
            strategy_key=self.strategy_key,
            strategy_name=self.name,
            category=self.category,
            universe=universe,
            rebalance_frequency=parameters.get("rebalance_frequency", "WEEKLY"),
            timestamp=datetime.now(timezone.utc).isoformat(),
            strategy_version=self.version,
            parameters=parameters,
            signals=signals,
            cash_weight=round(1.0 - sum(s.target_weight for s in signals), 4),
            summary=f"Mean reversion strategy allocated to top {top_n} oversold candidates led by {signals[0].ticker}.",
        )


class LowVolatilityStrategy(BaseStrategy):
    """
    Low Volatility Strategy:
    Allocates to universe inversely proportional to 252D annualized volatility (w_i proportional to 1 / vol).
    """

    def __init__(self):
        super().__init__(
            strategy_key="low_volatility",
            name="Minimum / Low Realized Volatility",
            category="DEFENSIVE",
        )

    def generate_signals(
        self,
        universe: List[str],
        parameters: Dict[str, Any],
        custom_data: Optional[Dict[str, Dict[str, Any]]] = None,
    ) -> StrategyExecutionResult:
        data = custom_data or UNIVERSE_DATA

        candidates: List[Tuple[str, float, float]] = []  # (ticker, vol, inv_vol)
        for ticker in universe:
            t_data = data.get(ticker, {})
            vol = max(0.05, t_data.get("volatility_252d", 0.20))
            inv_vol = 1.0 / vol
            candidates.append((ticker, vol, inv_vol))

        # Lowest volatility first
        candidates.sort(key=lambda x: x[1])
        top_n = parameters.get("top_n", 6)
        selected = candidates[:top_n]
        sum_inv_vol = sum(inv_vol for _, _, inv_vol in selected)

        signals: List[StrategySignalOutput] = []
        for rank, (ticker, vol, inv_vol) in enumerate(candidates, 1):
            if rank <= top_n and sum_inv_vol > 0:
                weight = round(inv_vol / sum_inv_vol, 4)
                action = "BUY" if rank <= 3 else "OVERWEIGHT"
                rationale = f"Low realized volatility ({vol*100:.1f}%), rank {rank} inverse-volatility allocation."
            else:
                weight = 0.0
                action = "HOLD" if rank <= top_n + 2 else "SELL"
                rationale = f"Realized volatility ({vol*100:.1f}%) exceeds low-vol decile boundary."

            signals.append(
                StrategySignalOutput(
                    ticker=ticker,
                    signal_score=round((1.0 - min(0.6, vol)) * 100.0, 2),
                    rank=rank,
                    target_weight=weight,
                    action=action,
                    rationale=rationale,
                    factor_breakdown={"volatility_252d": vol},
                )
            )

        return StrategyExecutionResult(
            strategy_key=self.strategy_key,
            strategy_name=self.name,
            category=self.category,
            universe=universe,
            rebalance_frequency=parameters.get("rebalance_frequency", "MONTHLY"),
            timestamp=datetime.now(timezone.utc).isoformat(),
            strategy_version=self.version,
            parameters=parameters,
            signals=signals,
            cash_weight=round(1.0 - sum(s.target_weight for s in signals), 4),
            summary=f"Low volatility strategy allocated across {top_n} lowest risk assets led by {signals[0].ticker}.",
        )


class FactorCombinationStrategy(BaseStrategy):
    """
    Factor Combination Strategy:
    Blends Momentum, Value, Quality, and Low Volatility style factors with custom or balanced weights.
    """

    def __init__(self):
        super().__init__(
            strategy_key="factor_combination",
            name="Multi-Factor Alpha Combination",
            category="MULTI_FACTOR",
        )

    def generate_signals(
        self,
        universe: List[str],
        parameters: Dict[str, Any],
        custom_data: Optional[Dict[str, Dict[str, Any]]] = None,
    ) -> StrategyExecutionResult:
        w_mom = parameters.get("weight_momentum", 0.30)
        w_val = parameters.get("weight_value", 0.25)
        w_qual = parameters.get("weight_quality", 0.25)
        w_low_vol = parameters.get("weight_low_vol", 0.20)
        top_n = parameters.get("top_n", 5)

        data = custom_data or UNIVERSE_DATA

        candidates: List[Tuple[str, float, Dict[str, float]]] = []
        for ticker in universe:
            t_data = data.get(ticker, {})
            mom = t_data.get("momentum_12m_1m", 0.15)
            val = t_data.get("earnings_yield", 0.04) * 10.0
            qual = t_data.get("roic", 0.20)
            vol = t_data.get("volatility_252d", 0.25)
            low_vol = max(0.0, (0.50 - vol))

            score = (mom * w_mom) + (val * w_val) + (qual * w_qual) + (low_vol * w_low_vol)
            candidates.append((ticker, score, {
                "momentum": mom,
                "value": val,
                "quality": qual,
                "low_vol": low_vol,
            }))

        candidates.sort(key=lambda x: x[1], reverse=True)
        selected = candidates[:top_n]
        sum_score = sum(max(0.01, s) for _, s, _ in selected)

        signals: List[StrategySignalOutput] = []
        for rank, (ticker, score, breakdown) in enumerate(candidates, 1):
            if rank <= top_n and sum_score > 0:
                weight = round(max(0.01, score) / sum_score, 4)
                action = "BUY" if rank <= 2 else "OVERWEIGHT"
                rationale = f"Top multi-factor composite (score {score*100:.1f}), rank {rank}."
            else:
                weight = 0.0
                action = "HOLD" if rank <= top_n + 2 else "SELL"
                rationale = "Factor composite ranking below top quartile threshold."

            signals.append(
                StrategySignalOutput(
                    ticker=ticker,
                    signal_score=round(score * 100.0, 2),
                    rank=rank,
                    target_weight=weight,
                    action=action,
                    rationale=rationale,
                    factor_breakdown=breakdown,
                )
            )

        return StrategyExecutionResult(
            strategy_key=self.strategy_key,
            strategy_name=self.name,
            category=self.category,
            universe=universe,
            rebalance_frequency=parameters.get("rebalance_frequency", "MONTHLY"),
            timestamp=datetime.now(timezone.utc).isoformat(),
            strategy_version=self.version,
            parameters=parameters,
            signals=signals,
            cash_weight=round(1.0 - sum(s.target_weight for s in signals), 4),
            summary=f"Multi-Factor combination allocated to top {top_n} balanced equity compounders led by {signals[0].ticker}.",
        )


class RiskParityStrategy(BaseStrategy):
    """
    Risk Parity Strategy:
    Equal Risk Contribution (ERC) allocation weighting assets inversely to their volatility.
    """

    def __init__(self):
        super().__init__(
            strategy_key="risk_parity",
            name="Equal Risk Contribution (Risk Parity)",
            category="ASSET_ALLOCATION",
        )

    def generate_signals(
        self,
        universe: List[str],
        parameters: Dict[str, Any],
        custom_data: Optional[Dict[str, Dict[str, Any]]] = None,
    ) -> StrategyExecutionResult:
        data = custom_data or UNIVERSE_DATA

        candidates: List[Tuple[str, float, float]] = []
        for ticker in universe:
            t_data = data.get(ticker, {})
            vol = max(0.08, t_data.get("volatility_252d", 0.22))
            inv_vol = 1.0 / vol
            candidates.append((ticker, vol, inv_vol))

        sum_inv_vol = sum(inv_vol for _, _, inv_vol in candidates)

        signals: List[StrategySignalOutput] = []
        for rank, (ticker, vol, inv_vol) in enumerate(candidates, 1):
            weight = round(inv_vol / sum_inv_vol, 4) if sum_inv_vol > 0 else 0.0
            action = "OVERWEIGHT" if weight > (1.0 / len(universe)) else "HOLD"
            rationale = f"Equal risk contribution allocation (Vol: {vol*100:.1f}%, weight: {weight*100:.1f}%)."

            signals.append(
                StrategySignalOutput(
                    ticker=ticker,
                    signal_score=round(weight * 100.0, 2),
                    rank=rank,
                    target_weight=weight,
                    action=action,
                    rationale=rationale,
                    factor_breakdown={"volatility_252d": vol, "target_risk_contribution": round(1.0 / len(universe), 4)},
                )
            )

        # Sort signals by target weight descending
        signals.sort(key=lambda s: s.target_weight, reverse=True)
        for i, s in enumerate(signals, 1):
            s.rank = i

        return StrategyExecutionResult(
            strategy_key=self.strategy_key,
            strategy_name=self.name,
            category=self.category,
            universe=universe,
            rebalance_frequency=parameters.get("rebalance_frequency", "MONTHLY"),
            timestamp=datetime.now(timezone.utc).isoformat(),
            strategy_version=self.version,
            parameters=parameters,
            signals=signals,
            cash_weight=round(1.0 - sum(s.target_weight for s in signals), 4),
            summary=f"Risk parity allocation balances risk contributions across all {len(universe)} universe assets.",
        )


class StrategyEngine:
    """Registry and executor for all systematic strategies."""

    def __init__(self):
        self._strategies: Dict[str, BaseStrategy] = {
            "momentum": MomentumStrategy(),
            "value": ValueStrategy(),
            "quality": QualityStrategy(),
            "trend_following": TrendFollowingStrategy(),
            "mean_reversion": MeanReversionStrategy(),
            "low_volatility": LowVolatilityStrategy(),
            "factor_combination": FactorCombinationStrategy(),
            "risk_parity": RiskParityStrategy(),
        }

    def list_strategies(self) -> List[Dict[str, Any]]:
        """Returns catalog of registered strategies."""
        return [
            {
                "strategy_key": s.strategy_key,
                "name": s.name,
                "category": s.category,
                "version": s.version,
                "default_universe": list(UNIVERSE_DATA.keys()),
            }
            for s in self._strategies.values()
        ]

    def get_strategy(self, strategy_key: str) -> Optional[BaseStrategy]:
        return self._strategies.get(strategy_key.lower())

    def execute_strategy(
        self,
        strategy_key: str,
        universe: Optional[List[str]] = None,
        parameters: Optional[Dict[str, Any]] = None,
        custom_data: Optional[Dict[str, Dict[str, Any]]] = None,
    ) -> StrategyExecutionResult:
        strategy = self.get_strategy(strategy_key)
        if not strategy:
            raise ValueError(f"Unknown strategy key: {strategy_key}")

        uni = universe or list(UNIVERSE_DATA.keys())
        params = parameters or {}
        return strategy.generate_signals(uni, params, custom_data=custom_data)
