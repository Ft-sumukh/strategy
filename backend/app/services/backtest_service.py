"""
AEGIS INVEST — Backtesting Domain Service
Orchestrates systematic strategy backtest executions, persists equity curves & trade logs,
and executes multi-model strategy tournaments.
"""

from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional
import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.analytics.backtesting.engine import BacktestEngine
from app.analytics.strategies.engine import StrategyEngine
from app.models.backtest import BacktestConfig, BacktestEquityPoint, BacktestRun, BacktestTrade
from app.services.market_provider import get_market_data_provider


class BacktestService:
    """Domain service for backtesting and strategy performance verification."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.engine = BacktestEngine()
        self.strategy_engine = StrategyEngine()

    async def run_backtest(
        self,
        name: str,
        strategy_key: str,
        universe: List[str],
        start_date: datetime,
        end_date: datetime,
        initial_capital: float = 100000.0,
        rebalance_frequency: str = "MONTHLY",
        transaction_cost_bps: float = 10.0,
        slippage_bps: float = 5.0,
        max_position_weight: float = 0.35,
        parameters: Optional[Dict[str, Any]] = None,
        user_id: str = "default_user",
    ) -> Dict[str, Any]:
        """
        Executes a deterministic backtest and persists config, run, equity points, and trade logs.
        """
        # 1. Fetch market data for universe
        mkt_prov = get_market_data_provider()
        daily_bars_map: Dict[str, List[Dict[str, Any]]] = {}
        for ticker in universe:
            bars = await mkt_prov.fetch_historical_bars(ticker, start_date, end_date)
            daily_bars_map[ticker] = [
                {"timestamp": b.timestamp, "close": b.close, "open": b.open, "volume": b.volume}
                for b in bars
            ]

        # 2. Strategy Signal Function (Point-In-Time)
        def signal_gen(as_of_dt: datetime, assets: List[str], price_history: Dict[datetime, Dict[str, float]]) -> Dict[str, float]:
            # Construct historical price series strictly <= as_of_dt
            past_dates = sorted([d for d in price_history.keys() if d <= as_of_dt])
            target_weights: Dict[str, float] = {}

            if strategy_key == "momentum":
                # Rank top momentum
                scores = {}
                for a in assets:
                    prices = [price_history[d][a] for d in past_dates if a in price_history[d]]
                    if len(prices) >= 20:
                        scores[a] = (prices[-1] - prices[0]) / prices[0]
                    else:
                        scores[a] = 0.0
                sorted_assets = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:3]
                w = 1.0 / len(sorted_assets) if sorted_assets else 0.0
                for a, _ in sorted_assets:
                    target_weights[a] = w

            elif strategy_key == "low_volatility":
                # Inverse realized volatility weighting
                vols = {}
                for a in assets:
                    prices = [price_history[d][a] for d in past_dates if a in price_history[d]]
                    if len(prices) >= 10:
                        rets = [(prices[i] - prices[i - 1]) / prices[i - 1] for i in range(1, len(prices))]
                        vols[a] = float(sum(r ** 2 for r in rets) ** 0.5) if rets else 0.2
                    else:
                        vols[a] = 0.2
                inv_sum = sum(1.0 / max(v, 0.001) for v in vols.values())
                for a, v in vols.items():
                    target_weights[a] = (1.0 / max(v, 0.001)) / inv_sum

            else:
                # Default equal weight across universe
                w = 1.0 / len(assets) if assets else 0.0
                for a in assets:
                    target_weights[a] = w

            return target_weights

        # 3. Execute deterministic engine
        sim_result = self.engine.run_backtest(
            daily_prices=daily_bars_map,
            strategy_signal_generator=signal_gen,
            universe=universe,
            start_date=start_date,
            end_date=end_date,
            initial_capital=initial_capital,
            rebalance_frequency=rebalance_frequency,
            transaction_cost_bps=transaction_cost_bps,
            slippage_bps=slippage_bps,
            max_position_weight=max_position_weight,
        )

        # 4. Save to Database
        config_obj = BacktestConfig(
            name=name,
            strategy_key=strategy_key,
            universe=",".join(universe),
            start_date=start_date,
            end_date=end_date,
            initial_capital=initial_capital,
            rebalance_frequency=rebalance_frequency,
            transaction_cost_bps=transaction_cost_bps,
            slippage_bps=slippage_bps,
            max_position_weight=max_position_weight,
            parameters=parameters or {},
            user_id=user_id,
        )
        self.session.add(config_obj)
        await self.session.flush()

        run_obj = BacktestRun(
            config_id=config_obj.id,
            status="COMPLETED",
            total_return=sim_result["total_return"],
            cagr=sim_result["cagr"],
            annualized_volatility=sim_result["annualized_volatility"],
            sharpe_ratio=sim_result["sharpe_ratio"],
            sortino_ratio=sim_result["sortino_ratio"],
            max_drawdown=sim_result["max_drawdown"],
            calmar_ratio=sim_result["calmar_ratio"],
            win_rate=sim_result["win_rate"],
            turnover=sim_result["turnover"],
            trades_count=sim_result["trades_count"],
            benchmark_return=sim_result["benchmark_return"],
            alpha=sim_result["alpha"],
            beta=sim_result["beta"],
        )
        self.session.add(run_obj)
        await self.session.flush()

        # Save equity points
        for pt in sim_result.get("equity_points", []):
            pt_date = datetime.fromisoformat(pt["date"])
            self.session.add(BacktestEquityPoint(
                run_id=run_obj.id,
                date=pt_date,
                equity=pt["equity"],
                drawdown=pt["drawdown"],
                benchmark_equity=pt["benchmark_equity"],
            ))

        # Save trades
        for tr in sim_result.get("trades", []):
            tr_date = datetime.fromisoformat(tr["timestamp"])
            self.session.add(BacktestTrade(
                run_id=run_obj.id,
                ticker=tr["ticker"],
                timestamp=tr_date,
                side=tr["side"],
                shares=tr["shares"],
                price=tr["price"],
                transaction_cost=tr["transaction_cost"],
                slippage=tr["slippage"],
                target_weight=tr["target_weight"],
            ))

        await self.session.commit()

        return {
            "config_id": config_obj.id,
            "run_id": run_obj.id,
            "strategy_key": strategy_key,
            "metrics": sim_result,
        }

    async def list_backtests(self, user_id: str = "default_user") -> List[Dict[str, Any]]:
        stmt = (
            select(BacktestConfig)
            .where(BacktestConfig.user_id == user_id)
            .options(selectinload(BacktestConfig.runs))
            .order_by(BacktestConfig.created_at.desc())
        )
        res = await self.session.execute(stmt)
        configs = res.scalars().all()
        return [
            {
                "id": c.id,
                "name": c.name,
                "strategy_key": c.strategy_key,
                "universe": c.universe,
                "created_at": c.created_at.isoformat(),
                "runs_count": len(c.runs),
                "latest_sharpe": c.runs[-1].sharpe_ratio if c.runs else None,
                "latest_total_return": c.runs[-1].total_return if c.runs else None,
            }
            for c in configs
        ]
