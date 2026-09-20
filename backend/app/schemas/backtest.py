"""
AEGIS INVEST — Backtesting, Risk, Stress & Optimization Schemas
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


# Backtesting
class BacktestRequestSchema(BaseModel):
    name: str = "Systematic Strategy Backtest"
    strategy_key: str = "momentum"
    universe: List[str] = ["AAPL", "MSFT", "NVDA", "GOOG", "AMZN"]
    start_date: str = "2023-01-01"
    end_date: str = "2025-02-01"
    initial_capital: float = 100000.0
    rebalance_frequency: str = "MONTHLY"
    transaction_cost_bps: float = 10.0
    slippage_bps: float = 5.0
    max_position_weight: float = 0.35


# Risk
class RiskDecompositionRequestSchema(BaseModel):
    portfolio_id: str


# Stress Testing
class StressTestRequestSchema(BaseModel):
    portfolio_id: str
    scenario_key: str = "2008_GFC"


# Optimization
class OptimizationRequestSchema(BaseModel):
    portfolio_id: str
    objective: str = "MAX_SHARPE"
    min_weight: float = 0.02
    max_weight: float = 0.35
