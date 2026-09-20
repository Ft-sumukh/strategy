"""
AEGIS INVEST — Systematic Strategy & Tournament Domain Service
Manages strategy registry, signal execution, multi-strategy tournament evaluations,
and reproducible experiment tracking.
"""

from datetime import datetime, timezone
import uuid
from typing import Any, Dict, List, Optional
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.analytics.strategies.engine import (
    StrategyEngine,
    StrategyExecutionResult,
    UNIVERSE_DATA,
)
from app.analytics.strategies.tournament import (
    BenchmarkComparison,
    StrategyTournament,
    StrategyTournamentResult,
)
from app.models.experiment import ExperimentRecord
from app.models.strategy import StrategyDefinition
from app.schemas.strategy import (
    BenchmarkComparisonOut,
    ExperimentCreateRequest,
    ExperimentRecordOut,
    StrategyDefinitionOut,
    StrategyRunRequest,
    StrategyRunResponse,
    StrategySignalOut,
    TournamentMetricsOut,
    TournamentRunRequest,
    TournamentRunResponse,
)


DEFAULT_STRATEGIES_CATALOG = [
    {
        "strategy_key": "momentum",
        "name": "Cross-Sectional Momentum",
        "category": "MOMENTUM",
        "description": "Ranks universe by 12M-1M return and allocates to top relative-strength momentum leaders.",
        "universe": list(UNIVERSE_DATA.keys()),
        "rebalance_frequency": "MONTHLY",
        "parameters": {"top_n": 5, "rebalance_frequency": "MONTHLY"},
        "risk_constraints": {"max_single_weight": 0.35, "min_single_weight": 0.05},
        "version": "1.0.0",
        "is_active": True,
    },
    {
        "strategy_key": "value",
        "name": "Composite Deep Value",
        "category": "VALUE",
        "description": "Blends earnings yield, free cash flow yield, and book-to-market to identify attractively priced equities.",
        "universe": list(UNIVERSE_DATA.keys()),
        "rebalance_frequency": "QUARTERLY",
        "parameters": {"top_n": 5, "rebalance_frequency": "QUARTERLY"},
        "risk_constraints": {"max_single_weight": 0.35, "min_single_weight": 0.05},
        "version": "1.0.0",
        "is_active": True,
    },
    {
        "strategy_key": "quality",
        "name": "High-Quality Compounders",
        "category": "QUALITY",
        "description": "Screens for high ROIC, high ROE, robust FCF margin, low accounting accruals, and prudent leverage.",
        "universe": list(UNIVERSE_DATA.keys()),
        "rebalance_frequency": "QUARTERLY",
        "parameters": {"top_n": 5, "rebalance_frequency": "QUARTERLY"},
        "risk_constraints": {"max_single_weight": 0.35, "min_single_weight": 0.05},
        "version": "1.0.0",
        "is_active": True,
    },
    {
        "strategy_key": "trend_following",
        "name": "Moving Average Trend Following",
        "category": "TREND",
        "description": "Trend filter requiring Price > SMA200 and SMA50 > SMA200 with ADX trend confirmation.",
        "universe": list(UNIVERSE_DATA.keys()),
        "rebalance_frequency": "MONTHLY",
        "parameters": {"min_adx": 20.0, "rebalance_frequency": "MONTHLY"},
        "risk_constraints": {"max_single_weight": 0.30, "min_single_weight": 0.05},
        "version": "1.0.0",
        "is_active": True,
    },
    {
        "strategy_key": "mean_reversion",
        "name": "Statistical Mean Reversion",
        "category": "MEAN_REVERSION",
        "description": "Detects short-term oversold conditions via RSI and Bollinger Band touches for mean-reversion bounces.",
        "universe": list(UNIVERSE_DATA.keys()),
        "rebalance_frequency": "WEEKLY",
        "parameters": {"rsi_threshold": 45.0, "top_n": 3, "rebalance_frequency": "WEEKLY"},
        "risk_constraints": {"max_single_weight": 0.40, "min_single_weight": 0.10},
        "version": "1.0.0",
        "is_active": True,
    },
    {
        "strategy_key": "low_volatility",
        "name": "Minimum / Low Realized Volatility",
        "category": "DEFENSIVE",
        "description": "Selects lowest 252-day annualized volatility assets with inverse-volatility weight scaling.",
        "universe": list(UNIVERSE_DATA.keys()),
        "rebalance_frequency": "MONTHLY",
        "parameters": {"top_n": 6, "rebalance_frequency": "MONTHLY"},
        "risk_constraints": {"max_single_weight": 0.30, "min_single_weight": 0.05},
        "version": "1.0.0",
        "is_active": True,
    },
    {
        "strategy_key": "factor_combination",
        "name": "Multi-Factor Alpha Combination",
        "category": "MULTI_FACTOR",
        "description": "Multi-factor composite blending Momentum, Value, Quality, and Low Volatility factors.",
        "universe": list(UNIVERSE_DATA.keys()),
        "rebalance_frequency": "MONTHLY",
        "parameters": {
            "weight_momentum": 0.30,
            "weight_value": 0.25,
            "weight_quality": 0.25,
            "weight_low_vol": 0.20,
            "top_n": 5,
            "rebalance_frequency": "MONTHLY",
        },
        "risk_constraints": {"max_single_weight": 0.35, "min_single_weight": 0.05},
        "version": "1.0.0",
        "is_active": True,
    },
    {
        "strategy_key": "risk_parity",
        "name": "Equal Risk Contribution (Risk Parity)",
        "category": "ASSET_ALLOCATION",
        "description": "Equal Risk Contribution allocation weighting assets inversely to their volatility across the full universe.",
        "universe": list(UNIVERSE_DATA.keys()),
        "rebalance_frequency": "MONTHLY",
        "parameters": {"rebalance_frequency": "MONTHLY"},
        "risk_constraints": {"max_single_weight": 0.40, "min_single_weight": 0.02},
        "version": "1.0.0",
        "is_active": True,
    },
]


class StrategyService:
    """Domain service for systematic strategies, tournaments, and experiments."""

    def __init__(self, session: Optional[AsyncSession] = None):
        self.session = session
        self.engine = StrategyEngine()
        self.tournament = StrategyTournament(self.engine)

    async def list_strategies(self) -> List[StrategyDefinitionOut]:
        """Lists all registered strategies."""
        if self.session:
            stmt = select(StrategyDefinition).order_by(StrategyDefinition.strategy_key)
            res = await self.session.execute(stmt)
            records = res.scalars().all()
            if records:
                return [
                    StrategyDefinitionOut(
                        strategy_key=r.strategy_key,
                        name=r.name,
                        category=r.category,
                        description=r.description,
                        universe=r.universe or list(UNIVERSE_DATA.keys()),
                        rebalance_frequency=r.rebalance_frequency,
                        parameters=r.parameters or {},
                        risk_constraints=r.risk_constraints or {},
                        version=r.version,
                        is_active=r.is_active,
                    )
                    for r in records
                ]

        # Return catalog default
        return [
            StrategyDefinitionOut(
                strategy_key=d["strategy_key"],
                name=d["name"],
                category=d["category"],
                description=d["description"],
                universe=d["universe"],
                rebalance_frequency=d["rebalance_frequency"],
                parameters=d["parameters"],
                risk_constraints=d["risk_constraints"],
                version=d["version"],
                is_active=d["is_active"],
            )
            for d in DEFAULT_STRATEGIES_CATALOG
        ]

    async def get_strategy(self, strategy_key: str) -> Optional[StrategyDefinitionOut]:
        """Retrieves a single strategy definition."""
        key_lower = strategy_key.lower()
        if self.session:
            stmt = select(StrategyDefinition).where(StrategyDefinition.strategy_key == key_lower)
            res = await self.session.execute(stmt)
            r = res.scalar_one_or_none()
            if r:
                return StrategyDefinitionOut(
                    strategy_key=r.strategy_key,
                    name=r.name,
                    category=r.category,
                    description=r.description,
                    universe=r.universe or list(UNIVERSE_DATA.keys()),
                    rebalance_frequency=r.rebalance_frequency,
                    parameters=r.parameters or {},
                    risk_constraints=r.risk_constraints or {},
                    version=r.version,
                    is_active=r.is_active,
                )

        # Fallback to catalog
        for d in DEFAULT_STRATEGIES_CATALOG:
            if d["strategy_key"] == key_lower:
                return StrategyDefinitionOut(
                    strategy_key=d["strategy_key"],
                    name=d["name"],
                    category=d["category"],
                    description=d["description"],
                    universe=d["universe"],
                    rebalance_frequency=d["rebalance_frequency"],
                    parameters=d["parameters"],
                    risk_constraints=d["risk_constraints"],
                    version=d["version"],
                    is_active=d["is_active"],
                )
        return None

    async def run_strategy(
        self,
        strategy_key: str,
        request: StrategyRunRequest,
    ) -> StrategyRunResponse:
        """Executes a single strategy with specified parameters and universe."""
        strat_def = await self.get_strategy(strategy_key)
        universe = request.universe or (strat_def.universe if strat_def else list(UNIVERSE_DATA.keys()))
        params = request.parameters or (strat_def.parameters if strat_def else {})
        if request.rebalance_frequency:
            params["rebalance_frequency"] = request.rebalance_frequency

        res: StrategyExecutionResult = self.engine.execute_strategy(
            strategy_key=strategy_key,
            universe=universe,
            parameters=params,
        )

        signals = [
            StrategySignalOut(
                ticker=s.ticker,
                signal_score=s.signal_score,
                rank=s.rank,
                target_weight=s.target_weight,
                action=s.action,
                rationale=s.rationale,
                factor_breakdown=s.factor_breakdown,
            )
            for s in res.signals
        ]

        return StrategyRunResponse(
            strategy_key=res.strategy_key,
            strategy_name=res.strategy_name,
            category=res.category,
            universe=res.universe,
            rebalance_frequency=res.rebalance_frequency,
            timestamp=res.timestamp,
            strategy_version=res.strategy_version,
            parameters=res.parameters,
            signals=signals,
            cash_weight=res.cash_weight,
            summary=res.summary,
        )

    async def run_tournament(
        self,
        request: Optional[TournamentRunRequest] = None,
    ) -> TournamentRunResponse:
        """Executes uniform multi-strategy tournament evaluation."""
        req = request or TournamentRunRequest()

        res: StrategyTournamentResult = self.tournament.run_tournament(
            universe=req.universe,
            evaluation_window=req.evaluation_window or "3Y",
            rebalance_frequency=req.rebalance_frequency or "MONTHLY",
            transaction_cost_bps=req.transaction_cost_bps or 10.0,
            slippage_bps=req.slippage_bps or 5.0,
            risk_free_rate_pct=req.risk_free_rate_pct or 4.5,
        )

        leaderboard = [
            TournamentMetricsOut(
                strategy_key=m.strategy_key,
                strategy_name=m.strategy_name,
                category=m.category,
                annualized_return=m.annualized_return,
                annualized_volatility=m.annualized_volatility,
                sharpe_ratio=m.sharpe_ratio,
                sortino_ratio=m.sortino_ratio,
                max_drawdown=m.max_drawdown,
                calmar_ratio=m.calmar_ratio,
                turnover_annual=m.turnover_annual,
                win_rate=m.win_rate,
                beta_to_market=m.beta_to_market,
                information_ratio=m.information_ratio,
                net_cost_drag_bps=m.net_cost_drag_bps,
                target_asset_count=m.target_asset_count,
                status=m.status,
            )
            for m in res.leaderboard
        ]

        benchmark = BenchmarkComparisonOut(
            name=res.benchmark.name,
            annualized_return=res.benchmark.annualized_return,
            annualized_volatility=res.benchmark.annualized_volatility,
            sharpe_ratio=res.benchmark.sharpe_ratio,
            max_drawdown=res.benchmark.max_drawdown,
        )

        return TournamentRunResponse(
            tournament_id=res.tournament_id,
            timestamp=res.timestamp,
            universe=res.universe,
            evaluation_window=res.evaluation_window,
            rebalance_frequency=res.rebalance_frequency,
            transaction_cost_bps=res.transaction_cost_bps,
            slippage_bps=res.slippage_bps,
            risk_free_rate_pct=res.risk_free_rate_pct,
            benchmark=benchmark,
            leaderboard=leaderboard,
            multi_objective_leaders=res.multi_objective_leaders,
            tradeoff_matrix=res.tradeoff_matrix,
            methodology=res.methodology,
        )

    async def list_experiments(self) -> List[ExperimentRecordOut]:
        """Lists research lab experiments."""
        if self.session:
            stmt = select(ExperimentRecord).order_by(desc(ExperimentRecord.created_at)).limit(50)
            res = await self.session.execute(stmt)
            records = res.scalars().all()
            if records:
                return [
                    ExperimentRecordOut(
                        id=str(r.id),
                        name=r.name,
                        hypothesis=r.hypothesis,
                        strategy_key=r.strategy_key,
                        parameters=r.parameters or {},
                        date_range=r.date_range,
                        rebalance_frequency=r.rebalance_frequency,
                        transaction_cost_bps=r.transaction_cost_bps,
                        slippage_bps=r.slippage_bps,
                        dataset_version=r.dataset_version,
                        strategy_version=r.strategy_version,
                        status=r.status,
                        results=r.results,
                        created_at=r.created_at,
                    )
                    for r in records
                ]

        # Default demo experiments
        return [
            ExperimentRecordOut(
                id="exp_mom_rebal_01",
                name="Momentum Rebalance Frequency Sensitivity",
                hypothesis="Monthly rebalancing captures trend persistence with lower turnover drag than weekly rebalancing.",
                strategy_key="momentum",
                parameters={"top_n": 5, "rebalance_frequency": "MONTHLY"},
                date_range="3Y",
                rebalance_frequency="MONTHLY",
                transaction_cost_bps=10.0,
                slippage_bps=5.0,
                dataset_version="v2.4",
                strategy_version="1.0.0",
                status="COMPLETED",
                results={
                    "annualized_return": 22.8,
                    "sharpe_ratio": 0.94,
                    "turnover": 185.0,
                    "conclusion": "Hypothesis confirmed. Monthly rebalancing reduced turnover drag by 92 bps.",
                },
                created_at=datetime.now(timezone.utc),
            ),
            ExperimentRecordOut(
                id="exp_qual_accruals_02",
                name="Quality Accruals Anomaly Isolation",
                hypothesis="Excluding firms with top decile Sloan accruals reduces max drawdown during market drawdowns.",
                strategy_key="quality",
                parameters={"top_n": 5, "filter_accruals": True},
                date_range="3Y",
                rebalance_frequency="QUARTERLY",
                transaction_cost_bps=10.0,
                slippage_bps=5.0,
                dataset_version="v2.4",
                strategy_version="1.0.0",
                status="COMPLETED",
                results={
                    "annualized_return": 19.6,
                    "sharpe_ratio": 0.99,
                    "max_drawdown": -14.8,
                    "conclusion": "Hypothesis supported. Low-accrual filtering cushioned drawdown by 2.4%.",
                },
                created_at=datetime.now(timezone.utc),
            ),
        ]

    async def create_experiment(self, req: ExperimentCreateRequest) -> ExperimentRecordOut:
        """Records and executes a new research lab experiment."""
        exp_id = f"exp_{uuid.uuid4().hex[:12]}"

        # Run the strategy evaluation for this experiment
        run_res = await self.run_strategy(
            strategy_key=req.strategy_key,
            request=StrategyRunRequest(
                parameters=req.parameters,
                rebalance_frequency=req.rebalance_frequency,
            ),
        )

        results = {
            "strategy_key": run_res.strategy_key,
            "signals_count": len(run_res.signals),
            "cash_weight": run_res.cash_weight,
            "top_asset": run_res.signals[0].ticker if run_res.signals else None,
            "top_signal_score": run_res.signals[0].signal_score if run_res.signals else None,
            "execution_status": "SUCCESS",
        }

        record = ExperimentRecordOut(
            id=exp_id,
            name=req.name,
            hypothesis=req.hypothesis,
            strategy_key=req.strategy_key,
            parameters=req.parameters or {},
            date_range=req.date_range or "3Y",
            rebalance_frequency=req.rebalance_frequency or "MONTHLY",
            transaction_cost_bps=req.transaction_cost_bps or 10.0,
            slippage_bps=req.slippage_bps or 5.0,
            dataset_version="v2.4",
            strategy_version="1.0.0",
            status="COMPLETED",
            results=results,
            created_at=datetime.now(timezone.utc),
        )

        if self.session:
            db_exp = ExperimentRecord(
                id=uuid.UUID(hex=exp_id.replace("exp_", "").ljust(32, "0")),
                name=req.name,
                hypothesis=req.hypothesis,
                strategy_key=req.strategy_key,
                parameters=req.parameters or {},
                date_range=req.date_range or "3Y",
                rebalance_frequency=req.rebalance_frequency or "MONTHLY",
                transaction_cost_bps=req.transaction_cost_bps or 10.0,
                slippage_bps=req.slippage_bps or 5.0,
                dataset_version="v2.4",
                strategy_version="1.0.0",
                status="COMPLETED",
                results=results,
            )
            self.session.add(db_exp)
            await self.session.commit()

        return record
