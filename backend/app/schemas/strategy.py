"""
AEGIS INVEST — Systematic Strategy & Experiment Schemas
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import Field
from app.schemas.common import BaseSchema


class StrategyDefinitionOut(BaseSchema):
    strategy_key: str
    name: str
    category: str
    description: Optional[str] = None
    universe: List[str] = Field(default_factory=list)
    rebalance_frequency: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    risk_constraints: Dict[str, Any] = Field(default_factory=dict)
    version: str
    is_active: bool


class StrategySignalOut(BaseSchema):
    ticker: str
    signal_score: float
    rank: int
    target_weight: float
    action: str
    rationale: str
    factor_breakdown: Dict[str, float] = Field(default_factory=dict)


class StrategyRunRequest(BaseSchema):
    universe: Optional[List[str]] = None
    parameters: Optional[Dict[str, Any]] = None
    rebalance_frequency: Optional[str] = None


class StrategyRunResponse(BaseSchema):
    strategy_key: str
    strategy_name: str
    category: str
    universe: List[str]
    rebalance_frequency: str
    timestamp: str
    strategy_version: str
    parameters: Dict[str, Any]
    signals: List[StrategySignalOut]
    cash_weight: float
    summary: str
    disclaimer: str = (
        "Systematic strategy signals are algorithmic outputs generated strictly from historical factors and parameters. "
        "They do not constitute financial advice, investment mandates, or performance guarantees."
    )


class TournamentRunRequest(BaseSchema):
    universe: Optional[List[str]] = None
    evaluation_window: Optional[str] = "3Y"
    rebalance_frequency: Optional[str] = "MONTHLY"
    transaction_cost_bps: Optional[float] = 10.0
    slippage_bps: Optional[float] = 5.0
    risk_free_rate_pct: Optional[float] = 4.5


class TournamentMetricsOut(BaseSchema):
    strategy_key: str
    strategy_name: str
    category: str
    annualized_return: float
    annualized_volatility: float
    sharpe_ratio: float
    sortino_ratio: float
    max_drawdown: float
    calmar_ratio: float
    turnover_annual: float
    win_rate: float
    beta_to_market: float
    information_ratio: float
    net_cost_drag_bps: float
    target_asset_count: int
    status: str = "PRELIMINARY"


class BenchmarkComparisonOut(BaseSchema):
    name: str
    annualized_return: float
    annualized_volatility: float
    sharpe_ratio: float
    max_drawdown: float


class TournamentRunResponse(BaseSchema):
    tournament_id: str
    timestamp: str
    universe: List[str]
    evaluation_window: str
    rebalance_frequency: str
    transaction_cost_bps: float
    slippage_bps: float
    risk_free_rate_pct: float
    benchmark: BenchmarkComparisonOut
    leaderboard: List[TournamentMetricsOut]
    multi_objective_leaders: Dict[str, str]
    tradeoff_matrix: List[Dict[str, Any]]
    methodology: str
    disclaimer: str = (
        "Tournament metrics are simulated historical strategy evaluations reflecting friction, slippage, and rebalancing costs. "
        "They do not represent live account executions or guaranteed returns."
    )


class ExperimentCreateRequest(BaseSchema):
    name: str = Field(min_length=3, max_length=120)
    hypothesis: str = Field(min_length=5, max_length=500)
    strategy_key: str
    parameters: Optional[Dict[str, Any]] = None
    date_range: Optional[str] = "3Y"
    rebalance_frequency: Optional[str] = "MONTHLY"
    transaction_cost_bps: Optional[float] = 10.0
    slippage_bps: Optional[float] = 5.0


class ExperimentRecordOut(BaseSchema):
    id: str
    name: str
    hypothesis: str
    strategy_key: str
    parameters: Dict[str, Any]
    date_range: str
    rebalance_frequency: str
    transaction_cost_bps: float
    slippage_bps: float
    dataset_version: str
    strategy_version: str
    status: str
    results: Optional[Dict[str, Any]] = None
    created_at: datetime
