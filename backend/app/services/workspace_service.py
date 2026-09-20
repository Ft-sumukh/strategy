"""
AEGIS INVEST — Research Workspace Domain Service
Manages Watchlists, Proactive Alert Rules & Events, Versioned Investment Theses,
and Analyst Research Report Generation.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.workspace import (
    AlertEvent,
    AlertRule,
    InvestmentThesis,
    ModelRegistryItem,
    ResearchReport,
    ThesisVersion,
    Watchlist,
    WatchlistItem,
)


class WorkspaceService:
    """Domain service for research workspace, watchlists, alerts, and thesis tracking."""

    def __init__(self, session: AsyncSession):
        self.session = session

    # --------------------------------------------------------------------------
    # Watchlist Management
    # --------------------------------------------------------------------------
    async def list_watchlists(self, user_id: str = "default_user") -> List[Watchlist]:
        stmt = (
            select(Watchlist)
            .where(Watchlist.user_id == user_id)
            .options(selectinload(Watchlist.items))
            .order_by(Watchlist.display_order.asc(), Watchlist.created_at.desc())
        )
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def get_watchlist(self, watchlist_id: str, user_id: str = "default_user") -> Optional[Watchlist]:
        stmt = (
            select(Watchlist)
            .where(Watchlist.id == watchlist_id, Watchlist.user_id == user_id)
            .options(selectinload(Watchlist.items))
        )
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def create_watchlist(
        self,
        name: str,
        description: Optional[str] = None,
        tickers: Optional[List[str]] = None,
        user_id: str = "default_user",
    ) -> Watchlist:
        wl = Watchlist(name=name, description=description, user_id=user_id)
        self.session.add(wl)
        await self.session.flush()

        if tickers:
            for t in tickers:
                item = WatchlistItem(watchlist_id=wl.id, ticker=t.upper())
                self.session.add(item)

        await self.session.commit()
        return await self.get_watchlist(wl.id, user_id)  # type: ignore

    async def add_watchlist_item(
        self,
        watchlist_id: str,
        ticker: str,
        target_price: Optional[float] = None,
        notes: Optional[str] = None,
        user_id: str = "default_user",
    ) -> Optional[WatchlistItem]:
        wl = await self.get_watchlist(watchlist_id, user_id)
        if not wl:
            return None
        item = WatchlistItem(
            watchlist_id=wl.id,
            ticker=ticker.upper(),
            target_price=target_price,
            notes=notes,
        )
        self.session.add(item)
        await self.session.commit()
        return item

    async def remove_watchlist_item(self, watchlist_id: str, ticker: str, user_id: str = "default_user") -> bool:
        wl = await self.get_watchlist(watchlist_id, user_id)
        if not wl:
            return False
        for it in wl.items:
            if it.ticker == ticker.upper():
                await self.session.delete(it)
                await self.session.commit()
                return True
        return False

    # --------------------------------------------------------------------------
    # Alert Rules & Events
    # --------------------------------------------------------------------------
    async def list_alerts(self, user_id: str = "default_user") -> List[AlertRule]:
        stmt = (
            select(AlertRule)
            .where(AlertRule.user_id == user_id)
            .options(selectinload(AlertRule.events))
            .order_by(AlertRule.created_at.desc())
        )
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def create_alert(
        self,
        alert_type: str,
        condition: str,
        threshold: str,
        ticker: Optional[str] = None,
        portfolio_id: Optional[str] = None,
        user_id: str = "default_user",
    ) -> AlertRule:
        rule = AlertRule(
            user_id=user_id,
            ticker=ticker.upper() if ticker else None,
            portfolio_id=portfolio_id,
            alert_type=alert_type,
            condition=condition,
            threshold=threshold,
            status="ACTIVE",
        )
        self.session.add(rule)
        await self.session.commit()
        return rule

    async def trigger_demo_event(self, rule_id: str, title: str, message: str, observed_val: str) -> AlertEvent:
        evt = AlertEvent(
            rule_id=rule_id,
            title=title,
            message=message,
            observed_value=observed_val,
        )
        self.session.add(evt)
        await self.session.commit()
        return evt

    # --------------------------------------------------------------------------
    # Investment Theses with Historical Versioning & Invalidation
    # --------------------------------------------------------------------------
    async def list_theses(self, user_id: str = "default_user") -> List[InvestmentThesis]:
        stmt = (
            select(InvestmentThesis)
            .where(InvestmentThesis.user_id == user_id)
            .options(selectinload(InvestmentThesis.versions))
            .order_by(InvestmentThesis.updated_at.desc())
        )
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def get_thesis(self, thesis_id: str, user_id: str = "default_user") -> Optional[InvestmentThesis]:
        stmt = (
            select(InvestmentThesis)
            .where(InvestmentThesis.id == thesis_id, InvestmentThesis.user_id == user_id)
            .options(selectinload(InvestmentThesis.versions))
        )
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def create_thesis(
        self,
        ticker: str,
        title: str,
        summary: str,
        investment_case: str,
        time_horizon: str = "1-3 Years",
        key_assumptions: Optional[List[str]] = None,
        supporting_evidence: Optional[List[Dict[str, Any]]] = None,
        contradicting_evidence: Optional[List[Dict[str, Any]]] = None,
        invalidation_conditions: Optional[List[str]] = None,
        user_id: str = "default_user",
    ) -> InvestmentThesis:
        thesis = InvestmentThesis(
            user_id=user_id,
            ticker=ticker.upper(),
            title=title,
            summary=summary,
            investment_case=investment_case,
            time_horizon=time_horizon,
            key_assumptions=key_assumptions or [],
            supporting_evidence=supporting_evidence or [],
            contradicting_evidence=contradicting_evidence or [],
            invalidation_conditions=invalidation_conditions or [
                "Operating margin compresses >300 bps",
                "Customer Capex growth turns negative",
                "Debt/EBITDA exceeds 3.0x",
            ],
            status="ACTIVE",
            version=1,
        )
        self.session.add(thesis)
        await self.session.flush()

        # Create Version 1 snapshot
        v1 = ThesisVersion(
            thesis_id=thesis.id,
            version_number=1,
            snapshot={
                "title": title,
                "summary": summary,
                "investment_case": investment_case,
                "key_assumptions": key_assumptions or [],
            },
            change_rationale="Initial thesis creation.",
        )
        self.session.add(v1)
        await self.session.commit()
        return await self.get_thesis(thesis.id, user_id)  # type: ignore

    async def update_thesis(
        self,
        thesis_id: str,
        title: Optional[str] = None,
        summary: Optional[str] = None,
        investment_case: Optional[str] = None,
        status: Optional[str] = None,
        change_rationale: Optional[str] = None,
        user_id: str = "default_user",
    ) -> Optional[InvestmentThesis]:
        thesis = await self.get_thesis(thesis_id, user_id)
        if not thesis:
            return None

        if title is not None:
            thesis.title = title
        if summary is not None:
            thesis.summary = summary
        if investment_case is not None:
            thesis.investment_case = investment_case
        if status is not None:
            thesis.status = status

        thesis.version += 1

        # Create new version snapshot (never overwrite historical version)
        ver = ThesisVersion(
            thesis_id=thesis.id,
            version_number=thesis.version,
            snapshot={
                "title": thesis.title,
                "summary": thesis.summary,
                "investment_case": thesis.investment_case,
                "status": thesis.status,
            },
            change_rationale=change_rationale or f"Updated to version {thesis.version}",
        )
        self.session.add(ver)
        await self.session.commit()
        return thesis

    # --------------------------------------------------------------------------
    # Research Reports
    # --------------------------------------------------------------------------
    async def list_reports(self, user_id: str = "default_user") -> List[ResearchReport]:
        stmt = (
            select(ResearchReport)
            .where(ResearchReport.user_id == user_id)
            .order_by(ResearchReport.created_at.desc())
        )
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def create_report(
        self,
        report_type: str,
        subject_id: str,
        title: str,
        executive_summary: str,
        content_sections: Optional[Dict[str, Any]] = None,
        evidence_citations: Optional[List[Dict[str, Any]]] = None,
        user_id: str = "default_user",
    ) -> ResearchReport:
        rep = ResearchReport(
            user_id=user_id,
            report_type=report_type,
            subject_id=subject_id.upper(),
            title=title,
            executive_summary=executive_summary,
            content_sections=content_sections or {},
            evidence_citations=evidence_citations or [],
            engine_versions={"valuation": "1.0", "technicals": "1.0", "factors": "1.0", "regime": "1.0"},
        )
        self.session.add(rep)
        await self.session.commit()
        return rep
