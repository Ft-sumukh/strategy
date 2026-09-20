"""
AEGIS INVEST — Research Reports & Exports Endpoints
"""

from typing import Any, Dict, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.workspace import ReportCreateSchema
from app.services.workspace_service import WorkspaceService

router = APIRouter(prefix="/reports", tags=["Research Reports"])


@router.get("")
async def list_reports(session: AsyncSession = Depends(get_db)):
    svc = WorkspaceService(session)
    reps = await svc.list_reports()
    return [
        {
            "id": r.id,
            "report_type": r.report_type,
            "subject_id": r.subject_id,
            "title": r.title,
            "executive_summary": r.executive_summary,
            "data_version": r.data_version,
            "created_at": r.created_at.isoformat() if r.created_at else "",
        }
        for r in reps
    ]


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_report(payload: ReportCreateSchema, session: AsyncSession = Depends(get_db)):
    svc = WorkspaceService(session)
    rep = await svc.create_report(
        report_type=payload.report_type,
        subject_id=payload.subject_id,
        title=payload.title,
        executive_summary=payload.executive_summary,
        content_sections=payload.content_sections,
    )
    return {
        "id": rep.id,
        "title": rep.title,
        "report_type": rep.report_type,
        "subject_id": rep.subject_id,
    }
