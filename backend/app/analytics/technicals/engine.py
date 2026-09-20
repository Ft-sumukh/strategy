"""
AEGIS INVEST — Technical Analysis Engine
Calculates standard institutional technical indicators:
SMA (20, 50, 100, 200), EMA (12, 26), RSI 14 (Wilder), MACD (12, 26, 9),
Bollinger Bands (20, 2), ATR 14, ADX 14, Volatility (annualized), Momentum,
and emits standardized TechnicalSignal objects.

Guidelines:
- No look-ahead bias: Indicators computed purely on historical time-series up to current bar.
- Clean float precision.
- Descriptive observations rather than guaranteed market predictions.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional
import math


@dataclass
class MovingAverages:
    sma_20: Optional[float] = None
    sma_50: Optional[float] = None
    sma_100: Optional[float] = None
    sma_200: Optional[float] = None
    ema_12: Optional[float] = None
    ema_26: Optional[float] = None


@dataclass
class RSIIndicator:
    rsi_14: Optional[float] = None
    status: str = "NEUTRAL"  # OVERBOUGHT, OVERSOLD, NEUTRAL
    interpretation: str = "Consolidation / In Range"


@dataclass
class MACDIndicator:
    macd_line: Optional[float] = None
    signal_line: Optional[float] = None
    histogram: Optional[float] = None
    status: str = "NEUTRAL"  # BULLISH, BEARISH, NEUTRAL


@dataclass
class BollingerBands:
    upper_band: Optional[float] = None
    middle_band: Optional[float] = None
    lower_band: Optional[float] = None
    bandwidth: Optional[float] = None
    percent_b: Optional[float] = None


@dataclass
class VolatilityAndTrend:
    atr_14: Optional[float] = None
    adx_14: Optional[float] = None
    trend_strength: str = "WEAK"  # STRONG_TREND, MODERATE_TREND, WEAK
    volatility_20d: Optional[float] = None  # Annualized
    volatility_60d: Optional[float] = None
    volatility_252d: Optional[float] = None


@dataclass
class MomentumMetrics:
    return_1m: Optional[float] = None
    return_3m: Optional[float] = None
    return_6m: Optional[float] = None
    return_1y: Optional[float] = None
    roc_14: Optional[float] = None


@dataclass
class TechnicalSignal:
    indicator: str
    value: float
    benchmark_threshold: str
    signal: str  # BULLISH, BEARISH, NEUTRAL
    rationale: str
    timestamp: str


@dataclass
class TechnicalAnalysisResult:
    ticker: str
    as_of_date: str
    latest_close: float
    moving_averages: MovingAverages
    rsi: RSIIndicator
    macd: MACDIndicator
    bollinger: BollingerBands
    volatility_and_trend: VolatilityAndTrend
    momentum: MomentumMetrics
    signals: List[TechnicalSignal] = field(default_factory=list)
    overall_sentiment: str = "NEUTRAL"  # BULLISH, BEARISH, NEUTRAL
    data_quality: str = "HIGH"


class TechnicalEngine:
    """Calculates deterministic technical analysis indicators and signals."""

    def _calc_sma(self, prices: List[float], period: int) -> Optional[float]:
        if len(prices) < period or period <= 0:
            return None
        window = prices[-period:]
        return sum(window) / float(period)

    def _calc_ema_series(self, prices: List[float], period: int) -> List[float]:
        if len(prices) < period or period <= 0:
            return []
        alpha = 2.0 / (period + 1.0)
        # First EMA is SMA of first 'period' bars
        ema_vals = [sum(prices[:period]) / float(period)]
        for p in prices[period:]:
            new_ema = p * alpha + ema_vals[-1] * (1.0 - alpha)
            ema_vals.append(new_ema)
        return ema_vals

    def _calc_rsi(self, closes: List[float], period: int = 14) -> Optional[float]:
        if len(closes) < period + 1:
            return None

        # Price changes
        changes = [closes[i] - closes[i - 1] for i in range(1, len(closes))]
        gains = [max(0.0, c) for c in changes]
        losses = [max(0.0, -c) for c in changes]

        # Initial averages
        avg_gain = sum(gains[:period]) / float(period)
        avg_loss = sum(losses[:period]) / float(period)

        # Wilder smoothing
        for i in range(period, len(changes)):
            avg_gain = (avg_gain * (period - 1) + gains[i]) / float(period)
            avg_loss = (avg_loss * (period - 1) + losses[i]) / float(period)

        if avg_loss == 0:
            return 100.0
        rs = avg_gain / avg_loss
        return 100.0 - (100.0 / (1.0 + rs))

    def _calc_macd(
        self, closes: List[float], fast: int = 12, slow: int = 26, signal_period: int = 9
    ) -> Tuple[Optional[float], Optional[float], Optional[float]]:
        if len(closes) < slow + signal_period:
            return None, None, None

        # Generate full EMA series
        alpha_fast = 2.0 / (fast + 1.0)
        alpha_slow = 2.0 / (slow + 1.0)

        # Build slow EMA
        slow_emas = [sum(closes[:slow]) / float(slow)]
        for p in closes[slow:]:
            slow_emas.append(p * alpha_slow + slow_emas[-1] * (1.0 - alpha_slow))

        # Build fast EMA aligned with slow EMA
        fast_emas = [sum(closes[slow - fast : slow]) / float(fast)]
        for p in closes[slow:]:
            fast_emas.append(p * alpha_fast + fast_emas[-1] * (1.0 - alpha_fast))

        # MACD Line series
        macd_series = [f - s for f, s in zip(fast_emas, slow_emas)]

        if len(macd_series) < signal_period:
            return None, None, None

        # Signal Line (EMA of MACD Line)
        alpha_sig = 2.0 / (signal_period + 1.0)
        sig_emas = [sum(macd_series[:signal_period]) / float(signal_period)]
        for m in macd_series[signal_period:]:
            sig_emas.append(m * alpha_sig + sig_emas[-1] * (1.0 - alpha_sig))

        latest_macd = macd_series[-1]
        latest_signal = sig_emas[-1]
        latest_hist = latest_macd - latest_signal

        return latest_macd, latest_signal, latest_hist

    def _calc_bollinger(self, closes: List[float], period: int = 20, k: float = 2.0) -> Tuple[Optional[float], Optional[float], Optional[float], Optional[float], Optional[float]]:
        if len(closes) < period:
            return None, None, None, None, None

        window = closes[-period:]
        mid = sum(window) / float(period)
        variance = sum((p - mid) ** 2 for p in window) / float(period)
        std = math.sqrt(variance)

        upper = mid + (k * std)
        lower = mid - (k * std)
        bandwidth = (upper - lower) / mid if mid > 0 else None

        last_p = closes[-1]
        percent_b = (last_p - lower) / (upper - lower) if (upper - lower) > 0 else 0.5

        return upper, mid, lower, bandwidth, percent_b

    def _calc_atr(self, highs: List[float], lows: List[float], closes: List[float], period: int = 14) -> Optional[float]:
        if len(closes) < period + 1 or len(highs) < period + 1 or len(lows) < period + 1:
            return None

        tr_list: List[float] = []
        for i in range(1, len(closes)):
            h = highs[i]
            l = lows[i]
            prev_c = closes[i - 1]
            tr = max(h - l, abs(h - prev_c), abs(l - prev_c))
            tr_list.append(tr)

        if len(tr_list) < period:
            return None

        atr = sum(tr_list[:period]) / float(period)
        for i in range(period, len(tr_list)):
            atr = (atr * (period - 1) + tr_list[i]) / float(period)

        return atr

    def _calc_adx(self, highs: List[float], lows: List[float], closes: List[float], period: int = 14) -> Optional[float]:
        if len(closes) < period * 2:
            return None

        tr_list = []
        plus_dm_list = []
        minus_dm_list = []

        for i in range(1, len(closes)):
            h = highs[i]
            l = lows[i]
            prev_h = highs[i - 1]
            prev_l = lows[i - 1]
            prev_c = closes[i - 1]

            tr = max(h - l, abs(h - prev_c), abs(l - prev_c))
            tr_list.append(tr)

            up_move = h - prev_h
            down_move = prev_l - l

            if up_move > down_move and up_move > 0:
                plus_dm_list.append(up_move)
            else:
                plus_dm_list.append(0.0)

            if down_move > up_move and down_move > 0:
                minus_dm_list.append(down_move)
            else:
                minus_dm_list.append(0.0)

        # Smooth TR, +DM, -DM
        smoothed_tr = sum(tr_list[:period])
        smoothed_plus_dm = sum(plus_dm_list[:period])
        smoothed_minus_dm = sum(minus_dm_list[:period])

        dx_list = []
        for i in range(period, len(tr_list)):
            smoothed_tr = smoothed_tr - (smoothed_tr / period) + tr_list[i]
            smoothed_plus_dm = smoothed_plus_dm - (smoothed_plus_dm / period) + plus_dm_list[i]
            smoothed_minus_dm = smoothed_minus_dm - (smoothed_minus_dm / period) + minus_dm_list[i]

            plus_di = (smoothed_plus_dm / smoothed_tr) * 100.0 if smoothed_tr > 0 else 0.0
            minus_di = (smoothed_minus_dm / smoothed_tr) * 100.0 if smoothed_tr > 0 else 0.0

            di_sum = plus_di + minus_di
            dx = (abs(plus_di - minus_di) / di_sum) * 100.0 if di_sum > 0 else 0.0
            dx_list.append(dx)

        if len(dx_list) < period:
            return None

        adx = sum(dx_list[:period]) / float(period)
        for i in range(period, len(dx_list)):
            adx = (adx * (period - 1) + dx_list[i]) / float(period)

        return adx

    def _calc_volatility(self, closes: List[float], window: int) -> Optional[float]:
        if len(closes) < window + 1:
            return None
        sub_closes = closes[-window - 1 :]
        returns = [(sub_closes[i] - sub_closes[i - 1]) / sub_closes[i - 1] for i in range(1, len(sub_closes))]
        mean_ret = sum(returns) / float(len(returns))
        var = sum((r - mean_ret) ** 2 for r in returns) / float(len(returns) - 1)
        daily_std = math.sqrt(var)
        return daily_std * math.sqrt(252.0)  # Annualized volatility

    def compute_technicals(self, ticker: str, bars: List[Any]) -> TechnicalAnalysisResult:
        """
        Takes raw MarketPriceBar objects (sorted ascending by timestamp)
        and computes complete technical analysis profile with signals.
        """
        if not bars:
            return TechnicalAnalysisResult(
                ticker=ticker,
                as_of_date="",
                latest_close=0.0,
                moving_averages=MovingAverages(),
                rsi=RSIIndicator(),
                macd=MACDIndicator(),
                bollinger=BollingerBands(),
                volatility_and_trend=VolatilityAndTrend(),
                momentum=MomentumMetrics(),
                data_quality="INSUFFICIENT_DATA",
            )

        closes = [float(b.close) for b in bars]
        highs = [float(b.high) for b in bars]
        lows = [float(b.low) for b in bars]
        latest_bar = bars[-1]
        as_of_date = str(latest_bar.timestamp)[:10]
        latest_close = closes[-1]

        # 1. Moving Averages
        sma_20 = self._calc_sma(closes, 20)
        sma_50 = self._calc_sma(closes, 50)
        sma_100 = self._calc_sma(closes, 100)
        sma_200 = self._calc_sma(closes, 200)

        ema_12_series = self._calc_ema_series(closes, 12)
        ema_26_series = self._calc_ema_series(closes, 26)
        ema_12 = ema_12_series[-1] if ema_12_series else None
        ema_26 = ema_26_series[-1] if ema_26_series else None

        ma_obj = MovingAverages(
            sma_20=round(sma_20, 2) if sma_20 else None,
            sma_50=round(sma_50, 2) if sma_50 else None,
            sma_100=round(sma_100, 2) if sma_100 else None,
            sma_200=round(sma_200, 2) if sma_200 else None,
            ema_12=round(ema_12, 2) if ema_12 else None,
            ema_26=round(ema_26, 2) if ema_26 else None,
        )

        # 2. RSI 14
        rsi_val = self._calc_rsi(closes, 14)
        rsi_status = "NEUTRAL"
        rsi_interp = "Consolidation / Within standard 30-70 band"
        if rsi_val is not None:
            if rsi_val >= 70.0:
                rsi_status = "OVERBOUGHT"
                rsi_interp = f"Elevated momentum (RSI {rsi_val:.1f} >= 70). Overbought conditions present."
            elif rsi_val <= 30.0:
                rsi_status = "OVERSOLD"
                rsi_interp = f"Depressed momentum (RSI {rsi_val:.1f} <= 30). Oversold conditions present."

        rsi_obj = RSIIndicator(
            rsi_14=round(rsi_val, 1) if rsi_val is not None else None,
            status=rsi_status,
            interpretation=rsi_interp,
        )

        # 3. MACD
        m_line, m_sig, m_hist = self._calc_macd(closes, 12, 26, 9)
        macd_status = "NEUTRAL"
        if m_hist is not None:
            if m_hist > 0:
                macd_status = "BULLISH"
            elif m_hist < 0:
                macd_status = "BEARISH"

        macd_obj = MACDIndicator(
            macd_line=round(m_line, 2) if m_line is not None else None,
            signal_line=round(m_sig, 2) if m_sig is not None else None,
            histogram=round(m_hist, 2) if m_hist is not None else None,
            status=macd_status,
        )

        # 4. Bollinger Bands
        bb_u, bb_m, bb_l, bb_bw, bb_pct = self._calc_bollinger(closes, 20, 2.0)
        boll_obj = BollingerBands(
            upper_band=round(bb_u, 2) if bb_u is not None else None,
            middle_band=round(bb_m, 2) if bb_m is not None else None,
            lower_band=round(bb_l, 2) if bb_l is not None else None,
            bandwidth=round(bb_bw, 4) if bb_bw is not None else None,
            percent_b=round(bb_pct, 3) if bb_pct is not None else None,
        )

        # 5. Volatility & Trend
        atr_14 = self._calc_atr(highs, lows, closes, 14)
        adx_14 = self._calc_adx(highs, lows, closes, 14)
        vol_20 = self._calc_volatility(closes, 20)
        vol_60 = self._calc_volatility(closes, 60)
        vol_252 = self._calc_volatility(closes, 252)

        trend_str = "WEAK"
        if adx_14 is not None:
            if adx_14 >= 25.0:
                trend_str = "STRONG_TREND"
            elif adx_14 >= 20.0:
                trend_str = "MODERATE_TREND"

        vol_trend_obj = VolatilityAndTrend(
            atr_14=round(atr_14, 2) if atr_14 is not None else None,
            adx_14=round(adx_14, 1) if adx_14 is not None else None,
            trend_strength=trend_str,
            volatility_20d=round(vol_20, 4) if vol_20 is not None else None,
            volatility_60d=round(vol_60, 4) if vol_60 is not None else None,
            volatility_252d=round(vol_252, 4) if vol_252 is not None else None,
        )

        # 6. Momentum Returns
        n_bars = len(closes)
        ret_1m = (latest_close - closes[-21]) / closes[-21] if n_bars >= 21 else None
        ret_3m = (latest_close - closes[-63]) / closes[-63] if n_bars >= 63 else None
        ret_6m = (latest_close - closes[-126]) / closes[-126] if n_bars >= 126 else None
        ret_1y = (latest_close - closes[-252]) / closes[-252] if n_bars >= 252 else None
        roc_14 = ((latest_close - closes[-14]) / closes[-14]) * 100.0 if n_bars >= 14 else None

        mom_obj = MomentumMetrics(
            return_1m=round(ret_1m, 4) if ret_1m is not None else None,
            return_3m=round(ret_3m, 4) if ret_3m is not None else None,
            return_6m=round(ret_6m, 4) if ret_6m is not None else None,
            return_1y=round(ret_1y, 4) if ret_1y is not None else None,
            roc_14=round(roc_14, 2) if roc_14 is not None else None,
        )

        # 7. Standardized Technical Signals
        signals: List[TechnicalSignal] = []

        # 200 SMA Signal
        if sma_200 is not None:
            if latest_close > sma_200:
                signals.append(TechnicalSignal(
                    indicator="SMA_200",
                    value=latest_close,
                    benchmark_threshold=f">{sma_200:.2f}",
                    signal="BULLISH",
                    rationale=f"Price ({latest_close:.2f}) is trading above the long-term 200-day moving average ({sma_200:.2f}).",
                    timestamp=as_of_date,
                ))
            else:
                signals.append(TechnicalSignal(
                    indicator="SMA_200",
                    value=latest_close,
                    benchmark_threshold=f"<{sma_200:.2f}",
                    signal="BEARISH",
                    rationale=f"Price ({latest_close:.2f}) is trading below the long-term 200-day moving average ({sma_200:.2f}).",
                    timestamp=as_of_date,
                ))

        # Golden / Death Cross Check
        if sma_50 is not None and sma_200 is not None:
            if sma_50 > sma_200:
                signals.append(TechnicalSignal(
                    indicator="GOLDEN_CROSS",
                    value=sma_50,
                    benchmark_threshold=f">{sma_200:.2f}",
                    signal="BULLISH",
                    rationale="50-day SMA is above 200-day SMA, indicating upward medium-term structural trend.",
                    timestamp=as_of_date,
                ))
            else:
                signals.append(TechnicalSignal(
                    indicator="DEATH_CROSS",
                    value=sma_50,
                    benchmark_threshold=f"<{sma_200:.2f}",
                    signal="BEARISH",
                    rationale="50-day SMA is below 200-day SMA, indicating downward medium-term structural trend.",
                    timestamp=as_of_date,
                ))

        # RSI Signal
        if rsi_val is not None:
            if rsi_val >= 70.0:
                signals.append(TechnicalSignal(
                    indicator="RSI_14",
                    value=rsi_val,
                    benchmark_threshold=">=70.0",
                    signal="BEARISH",
                    rationale=f"RSI ({rsi_val:.1f}) in overbought territory. Elevated risk of near-term consolidation.",
                    timestamp=as_of_date,
                ))
            elif rsi_val <= 30.0:
                signals.append(TechnicalSignal(
                    indicator="RSI_14",
                    value=rsi_val,
                    benchmark_threshold="<=30.0",
                    signal="BULLISH",
                    rationale=f"RSI ({rsi_val:.1f}) in oversold territory. Potential mean-reversion exhaustion.",
                    timestamp=as_of_date,
                ))
            else:
                signals.append(TechnicalSignal(
                    indicator="RSI_14",
                    value=rsi_val,
                    benchmark_threshold="30-70",
                    signal="NEUTRAL",
                    rationale=f"RSI ({rsi_val:.1f}) is balanced within standard neutral zone.",
                    timestamp=as_of_date,
                ))

        # MACD Signal
        if m_hist is not None:
            if m_hist > 0:
                signals.append(TechnicalSignal(
                    indicator="MACD_HISTOGRAM",
                    value=m_hist,
                    benchmark_threshold=">0.0",
                    signal="BULLISH",
                    rationale="MACD line is above the 9-day signal line, showing positive momentum acceleration.",
                    timestamp=as_of_date,
                ))
            else:
                signals.append(TechnicalSignal(
                    indicator="MACD_HISTOGRAM",
                    value=m_hist,
                    benchmark_threshold="<0.0",
                    signal="BEARISH",
                    rationale="MACD line is below the 9-day signal line, showing negative momentum acceleration.",
                    timestamp=as_of_date,
                ))

        # Overall Sentiment Determination
        bullish_cnt = sum(1 for s in signals if s.signal == "BULLISH")
        bearish_cnt = sum(1 for s in signals if s.signal == "BEARISH")
        if bullish_cnt > bearish_cnt:
            sentiment = "BULLISH"
        elif bearish_cnt > bullish_cnt:
            sentiment = "BEARISH"
        else:
            sentiment = "NEUTRAL"

        return TechnicalAnalysisResult(
            ticker=ticker,
            as_of_date=as_of_date,
            latest_close=round(latest_close, 2),
            moving_averages=ma_obj,
            rsi=rsi_obj,
            macd=macd_obj,
            bollinger=boll_obj,
            volatility_and_trend=vol_trend_obj,
            momentum=mom_obj,
            signals=signals,
            overall_sentiment=sentiment,
            data_quality="HIGH",
        )
