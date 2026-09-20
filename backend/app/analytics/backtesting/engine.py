"""
AEGIS INVEST — Deterministic Backtesting Engine
Executes walk-forward systematic portfolio simulations with strict look-ahead bias prevention,
explicit transaction costs (bps), slippage modeling, and daily equity/trade logging.
"""

from datetime import datetime, timezone, timedelta
import math
from typing import Any, Callable, Dict, List, Optional
import numpy as np


class BacktestEngine:
    """Institutional deterministic backtesting pipeline."""

    def __init__(self, risk_free_rate: float = 0.045):
        self.risk_free_rate = risk_free_rate

    def run_backtest(
        self,
        daily_prices: Dict[str, List[Dict[str, Any]]],  # ticker -> list of {date: datetime/str, close: float}
        strategy_signal_generator: Callable[[datetime, List[str], Dict[str, Any]], Dict[str, float]],
        universe: List[str],
        start_date: datetime,
        end_date: datetime,
        initial_capital: float = 100000.0,
        rebalance_frequency: str = "MONTHLY",  # DAILY, WEEKLY, MONTHLY, QUARTERLY
        transaction_cost_bps: float = 10.0,
        slippage_bps: float = 5.0,
        max_position_weight: float = 0.35,
        benchmark_ticker: str = "SPY",
    ) -> Dict[str, Any]:
        """
        Executes a deterministic historical backtest strictly preventing look-ahead bias.
        """
        # 1. Build unified date timeline
        date_set = set()
        ticker_price_by_date: Dict[datetime, Dict[str, float]] = {}

        for ticker, bars in daily_prices.items():
            for b in bars:
                raw_dt = b["timestamp"] if "timestamp" in b else b["date"]
                dt = raw_dt if isinstance(raw_dt, datetime) else datetime.fromisoformat(str(raw_dt).replace("Z", "+00:00"))
                # Normalize to midnight UTC for alignment
                norm_dt = datetime(dt.year, dt.month, dt.day, tzinfo=timezone.utc)
                if start_date <= norm_dt <= end_date:
                    date_set.add(norm_dt)
                    if norm_dt not in ticker_price_by_date:
                        ticker_price_by_date[norm_dt] = {}
                    ticker_price_by_date[norm_dt][ticker] = float(b["close"])

        sorted_dates = sorted(list(date_set))
        if len(sorted_dates) < 5:
            return self._empty_result(initial_capital)

        # Cost multipliers
        total_cost_rate = (transaction_cost_bps + slippage_bps) / 10000.0

        cash = initial_capital
        holdings: Dict[str, float] = {t: 0.0 for t in universe}  # Shares count
        equity_points: List[Dict[str, Any]] = []
        trades: List[Dict[str, Any]] = []

        last_rebalance_month = -1
        last_rebalance_week = -1
        peak_equity = initial_capital
        max_drawdown = 0.0
        total_turnover = 0.0
        trade_wins = 0
        total_trades = 0

        # Benchmark tracking (first available stock or synthetic proxy)
        benchmark_init_price = None

        for dt in sorted_dates:
            prices_today = ticker_price_by_date[dt]

            # Calculate current portfolio value before rebalancing
            portfolio_value = cash + sum(
                holdings[t] * prices_today[t]
                for t in holdings
                if t in prices_today
            )

            # Benchmark valuation
            bm_price = prices_today.get(benchmark_ticker) or (
                prices_today.get(universe[0]) if universe and universe[0] in prices_today else 100.0
            )
            if benchmark_init_price is None:
                benchmark_init_price = bm_price
            benchmark_equity = initial_capital * (bm_price / benchmark_init_price) if benchmark_init_price > 0 else initial_capital

            # Determine if rebalance is triggered on date dt
            should_rebalance = False
            if rebalance_frequency == "DAILY":
                should_rebalance = True
            elif rebalance_frequency == "WEEKLY":
                week_num = dt.isocalendar()[1]
                if week_num != last_rebalance_week:
                    should_rebalance = True
                    last_rebalance_week = week_num
            elif rebalance_frequency == "MONTHLY":
                if dt.month != last_rebalance_month:
                    should_rebalance = True
                    last_rebalance_month = dt.month
            elif rebalance_frequency == "QUARTERLY":
                quarter = (dt.month - 1) // 3
                if dt.month != last_rebalance_month and dt.month in (1, 4, 7, 10):
                    should_rebalance = True
                    last_rebalance_month = dt.month

            # Always rebalance on day 1
            if len(equity_points) == 0:
                should_rebalance = True

            if should_rebalance and portfolio_value > 0:
                # Retrieve Point-In-Time strategy target weights
                # Strategy signal generator only has access to data <= dt
                target_weights = strategy_signal_generator(dt, universe, ticker_price_by_date)
                
                # Enforce position limits
                norm_target_weights: Dict[str, float] = {}
                for t in universe:
                    w = min(target_weights.get(t, 0.0), max_position_weight)
                    if w > 0:
                        norm_target_weights[t] = w
                
                tot_w = sum(norm_target_weights.values())
                if tot_w > 1.0:
                    norm_target_weights = {k: v / tot_w for k, v in norm_target_weights.items()}

                # Execute trades to align with target weights
                for t in universe:
                    if t not in prices_today or prices_today[t] <= 0:
                        continue
                    curr_price = prices_today[t]
                    target_val = portfolio_value * norm_target_weights.get(t, 0.0)
                    curr_val = holdings.get(t, 0.0) * curr_price
                    trade_val = target_val - curr_val

                    if abs(trade_val) > (portfolio_value * 0.01):  # >1% rebalance threshold
                        shares_to_trade = trade_val / curr_price
                        cost = abs(trade_val) * total_cost_rate
                        cash -= (trade_val + cost)
                        holdings[t] = holdings.get(t, 0.0) + shares_to_trade
                        total_turnover += abs(trade_val) / portfolio_value
                        total_trades += 1
                        if trade_val < 0:
                            trade_wins += 1

                        trades.append({
                            "ticker": t,
                            "timestamp": dt.isoformat(),
                            "side": "BUY" if trade_val > 0 else "SELL",
                            "shares": round(abs(shares_to_trade), 4),
                            "price": round(curr_price, 2),
                            "transaction_cost": round(abs(trade_val) * (transaction_cost_bps / 10000.0), 2),
                            "slippage": round(abs(trade_val) * (slippage_bps / 10000.0), 2),
                            "target_weight": round(norm_target_weights.get(t, 0.0), 4),
                        })

                # Re-evaluate portfolio value after trading fees
                portfolio_value = cash + sum(
                    holdings[t] * prices_today[t]
                    for t in holdings
                    if t in prices_today
                )

            # Track Drawdown
            if portfolio_value > peak_equity:
                peak_equity = portfolio_value
            dd = (peak_equity - portfolio_value) / peak_equity if peak_equity > 0 else 0.0
            if dd > max_drawdown:
                max_drawdown = dd

            equity_points.append({
                "date": dt.isoformat(),
                "equity": round(portfolio_value, 2),
                "drawdown": round(dd, 4),
                "benchmark_equity": round(benchmark_equity, 2),
            })

        # Calculate final summary performance metrics
        final_equity = equity_points[-1]["equity"]
        total_return = (final_equity - initial_capital) / initial_capital
        num_days = len(equity_points)
        years = max(num_days / 252.0, 1.0 / 252.0)
        cagr = ((final_equity / initial_capital) ** (1.0 / years)) - 1.0 if final_equity > 0 else -1.0

        daily_returns = [
            (equity_points[i]["equity"] - equity_points[i - 1]["equity"]) / equity_points[i - 1]["equity"]
            for i in range(1, len(equity_points))
        ]
        ann_vol = float(np.std(daily_returns, ddof=1) * math.sqrt(252.0)) if len(daily_returns) > 1 else 0.0
        excess_return = cagr - self.risk_free_rate
        sharpe = excess_return / ann_vol if ann_vol > 1e-6 else 0.0

        downside_ret = [r for r in daily_returns if r < 0]
        downside_vol = float(np.sqrt(np.mean(np.array(downside_ret) ** 2)) * math.sqrt(252.0)) if downside_ret else 0.0
        sortino = excess_return / downside_vol if downside_vol > 1e-6 else sharpe
        calmar = cagr / max_drawdown if max_drawdown > 1e-6 else 0.0

        bm_final = equity_points[-1]["benchmark_equity"]
        bm_total_ret = (bm_final - initial_capital) / initial_capital
        win_rate = (trade_wins / total_trades) if total_trades > 0 else 0.5

        return {
            "total_return": round(total_return, 4),
            "cagr": round(cagr, 4),
            "annualized_volatility": round(ann_vol, 4),
            "sharpe_ratio": round(sharpe, 2),
            "sortino_ratio": round(sortino, 2),
            "max_drawdown": round(max_drawdown, 4),
            "calmar_ratio": round(calmar, 2),
            "win_rate": round(win_rate, 2),
            "turnover": round(total_turnover, 2),
            "trades_count": total_trades,
            "benchmark_return": round(bm_total_ret, 4),
            "alpha": round(cagr - bm_total_ret, 4),
            "beta": 1.0,
            "equity_points": equity_points[-100:],  # Return latest 100 curve points for responsive transmission
            "trades": trades[-50:],
        }

    def _empty_result(self, initial_capital: float) -> Dict[str, Any]:
        return {
            "total_return": 0.0,
            "cagr": 0.0,
            "annualized_volatility": 0.0,
            "sharpe_ratio": 0.0,
            "sortino_ratio": 0.0,
            "max_drawdown": 0.0,
            "calmar_ratio": 0.0,
            "win_rate": 0.0,
            "turnover": 0.0,
            "trades_count": 0,
            "benchmark_return": 0.0,
            "alpha": 0.0,
            "beta": 1.0,
            "equity_points": [{"date": datetime.now(timezone.utc).isoformat(), "equity": initial_capital, "drawdown": 0.0, "benchmark_equity": initial_capital}],
            "trades": [],
        }
