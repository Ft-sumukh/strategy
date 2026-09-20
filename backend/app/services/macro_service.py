"""
AEGIS INVEST — Macroeconomic Domain Service
Coordinates sovereign macroeconomic series, yield curve inversion tracking,
and asset-level macroeconomic sensitivity analysis.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.analytics.macro.sensitivity import AssetMacroSensitivity, MacroSensitivityEngine
from app.models.macro import MacroObservation, MacroSeries
from app.providers.macro.provider import DemoMacroDataProvider
from app.schemas.macro import (
    AssetMacroSensitivityOut,
    MacroObservationOut,
    MacroSensitivityFactorOut,
    MacroSeriesOut,
    YieldCurvePoint,
    YieldCurveResponse,
)


class MacroService:
    """Domain service for macroeconomic indicators and asset sensitivities."""

    def __init__(self, session: Optional[AsyncSession] = None):
        self.session = session
        self.provider = DemoMacroDataProvider()
        self.sensitivity_engine = MacroSensitivityEngine()

    async def list_series(self) -> List[MacroSeriesOut]:
        """Returns catalog of all tracked macroeconomic series."""
        if self.session:
            stmt = select(MacroSeries).order_by(MacroSeries.series_code)
            res = await self.session.execute(stmt)
            db_series = res.scalars().all()
            if db_series:
                out: List[MacroSeriesOut] = []
                for s in db_series:
                    latest = await self._get_latest_observation(s.series_code)
                    out.append(
                        MacroSeriesOut(
                            series_code=s.series_code,
                            name=s.name,
                            country=s.country,
                            frequency=s.frequency,
                            unit=s.unit,
                            description=s.description,
                            source=s.source,
                            latest_value=latest.value if latest else None,
                            latest_timestamp=latest.timestamp if latest else None,
                        )
                    )
                return out

        # Fallback to provider
        meta_list = self.provider.list_series()
        out = []
        for m in meta_list:
            latest = self.provider.get_latest_observation(m["series_code"])
            out.append(
                MacroSeriesOut(
                    series_code=m["series_code"],
                    name=m["name"],
                    country=m["country"],
                    frequency=m["frequency"],
                    unit=m["unit"],
                    description=m.get("description"),
                    source=m.get("source"),
                    latest_value=latest["value"] if latest else None,
                    latest_timestamp=datetime.fromisoformat(latest["timestamp"].replace("Z", "+00:00")) if latest else None,
                )
            )
        return out

    async def get_series_detail(self, series_code: str, limit: int = 100) -> Optional[MacroSeriesOut]:
        """Returns series metadata and observation history."""
        code_upper = series_code.upper()
        if self.session:
            stmt = select(MacroSeries).where(MacroSeries.series_code == code_upper)
            res = await self.session.execute(stmt)
            s = res.scalar_one_or_none()
            if s:
                obs_stmt = (
                    select(MacroObservation)
                    .where(MacroObservation.series_code == code_upper)
                    .order_by(desc(MacroObservation.timestamp))
                    .limit(limit)
                )
                obs_res = await self.session.execute(obs_stmt)
                obs_list = obs_res.scalars().all()

                history = [
                    MacroObservationOut(
                        series_code=o.series_code,
                        timestamp=o.timestamp,
                        value=o.value,
                        source=o.source,
                    )
                    for o in reversed(obs_list)
                ]
                latest = obs_list[0] if obs_list else None
                return MacroSeriesOut(
                    series_code=s.series_code,
                    name=s.name,
                    country=s.country,
                    frequency=s.frequency,
                    unit=s.unit,
                    description=s.description,
                    source=s.source,
                    latest_value=latest.value if latest else None,
                    latest_timestamp=latest.timestamp if latest else None,
                    history=history,
                )

        # Fallback to provider
        meta = self.provider.get_series_metadata(code_upper)
        if not meta:
            return None

        obs = self.provider.get_observations(code_upper, limit=limit)
        history = [
            MacroObservationOut(
                series_code=o["series_code"],
                timestamp=datetime.fromisoformat(o["timestamp"].replace("Z", "+00:00")),
                value=o["value"],
                source=o.get("source"),
            )
            for o in obs
        ]
        latest = obs[-1] if obs else None
        return MacroSeriesOut(
            series_code=meta["series_code"],
            name=meta["name"],
            country=meta["country"],
            frequency=meta["frequency"],
            unit=meta["unit"],
            description=meta.get("description"),
            source=meta.get("source"),
            latest_value=latest["value"] if latest else None,
            latest_timestamp=datetime.fromisoformat(latest["timestamp"].replace("Z", "+00:00")) if latest else None,
            history=history,
        )

    async def get_yield_curve(self) -> YieldCurveResponse:
        """Retrieves sovereign US Treasury yield curve and calculates inversion spread."""
        yc_data = self.provider.get_yield_curve()

        points = [
            YieldCurvePoint(
                tenor=p["tenor"],
                tenor_years=p["tenor_years"],
                yield_pct=p["yield_pct"],
                series_code=p["series_code"],
            )
            for p in yc_data.get("curve_points", [])
        ]

        spread = yc_data.get("spread_10y_2y", 0.18)
        is_inv = spread < 0.0
        depth = round(abs(spread) * 100.0, 1) if is_inv else 0.0

        if is_inv:
            regime = f"Inverted Yield Curve (10Y-2Y Spread: {spread * 100:+.0f} bps) — Historical Recession Precursor Signal"
        elif spread < 0.20:
            regime = f"Flat Yield Curve (10Y-2Y Spread: {spread * 100:+.0f} bps) — Late-Cycle / Tight Policy Posture"
        else:
            regime = f"Normal Upward-Sloping Yield Curve (10Y-2Y Spread: {spread * 100:+.0f} bps) — Cyclical Expansion Shape"

        return YieldCurveResponse(
            as_of_date=yc_data.get("as_of_date", datetime.now(timezone.utc).isoformat()),
            curve_points=points,
            spread_10y_2y=spread,
            is_inverted=is_inv,
            inversion_depth_bps=depth,
            regime_context=regime,
        )

    async def get_asset_sensitivity(self, ticker: str) -> AssetMacroSensitivityOut:
        """Computes statistical macroeconomic sensitivity for the specified ticker."""
        res: AssetMacroSensitivity = self.sensitivity_engine.analyze_asset_sensitivity(ticker)

        factors = [
            MacroSensitivityFactorOut(
                series_code=f.series_code,
                factor_name=f.factor_name,
                beta=f.beta,
                correlation=f.correlation,
                r_squared=f.r_squared,
                p_value=f.p_value,
                sample_size=f.sample_size,
                exposure_direction=f.exposure_direction,
                interpretation=f.interpretation,
                description=f.description,
            )
            for f in res.sensitivities
        ]

        return AssetMacroSensitivityOut(
            ticker=res.ticker,
            as_of_date=res.as_of_date,
            sample_period_days=res.sample_period_days,
            sensitivities=factors,
            dominant_macro_risk=res.dominant_macro_risk,
            resilience_score=res.resilience_score,
            data_quality=res.data_quality,
        )

    async def _get_latest_observation(self, series_code: str) -> Optional[MacroObservation]:
        if not self.session:
            return None
        stmt = (
            select(MacroObservation)
            .where(MacroObservation.series_code == series_code)
            .order_by(desc(MacroObservation.timestamp))
            .limit(1)
        )
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()
