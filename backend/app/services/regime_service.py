"""
AEGIS INVEST — Market Regime Domain Service
Orchestrates multi-indicator market regime evaluations and historical timelines.
"""

from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.analytics.regime.engine import (
    HistoricalRegimePeriod,
    RegimeDetectionEngine,
    RegimeEvaluationResult,
)
from app.schemas.regime import (
    HistoricalRegimePeriodOut,
    RegimeEvaluationOut,
    RegimeSignalDetailOut,
)


class RegimeService:
    """Domain service for market regime classification and historical timelines."""

    def __init__(self, session: Optional[AsyncSession] = None):
        self.session = session
        self.engine = RegimeDetectionEngine()

    async def get_current_regime(self) -> RegimeEvaluationOut:
        """Evaluates current observable market regime across trend, volatility, breadth, and credit."""
        res: RegimeEvaluationResult = self.engine.evaluate_regime()

        signals = [
            RegimeSignalDetailOut(
                signal_name=s.signal_name,
                category=s.category,
                value=s.value,
                unit=s.unit,
                state=s.state,
                weight=s.weight,
                description=s.description,
            )
            for s in res.supporting_signals
        ]

        timeline = [
            HistoricalRegimePeriodOut(
                start_date=h.start_date,
                end_date=h.end_date,
                regime=h.regime,
                duration_days=h.duration_days,
                primary_driver=h.primary_driver,
                average_vix=h.average_vix,
            )
            for h in res.historical_timeline
        ]

        return RegimeEvaluationOut(
            as_of_date=res.as_of_date,
            regime=res.regime,
            display_name=res.display_name,
            confidence=res.confidence,
            duration_days=res.duration_days,
            supporting_signals=signals,
            regime_characteristics=res.regime_characteristics,
            historical_timeline=timeline,
            methodology=res.methodology,
        )

    async def get_regime_history(self) -> List[HistoricalRegimePeriodOut]:
        """Returns the audited historical regime timeline."""
        return [
            HistoricalRegimePeriodOut(
                start_date=h.start_date,
                end_date=h.end_date,
                regime=h.regime,
                duration_days=h.duration_days,
                primary_driver=h.primary_driver,
                average_vix=h.average_vix,
            )
            for h in self.engine.BENCHMARK_TIMELINE
        ]
