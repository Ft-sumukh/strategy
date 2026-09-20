"""
AEGIS INVEST — AI Reasoning REST Endpoints
"""

from typing import Any, Dict
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.research.research_engine import ResearchAssistantEngine
from app.core.config import get_settings
from app.db.session import get_db
from app.models.ai import AIAuditLog
from app.schemas.ai import AIResearchRequestSchema, AIResearchResponseSchema

router = APIRouter(prefix="/ai", tags=["AI Decision Intelligence"])


@router.get("/status")
async def get_ai_status():
    """Returns safe operational status of the active LLM reasoning provider."""
    settings = get_settings()
    prov = (settings.llm_provider or "AEGIS_INTERNAL_DETERMINISTIC").upper()
    model = settings.llm_model or ("qwen3-32b" if prov == "QWEN" else "aegis-institutional-v1")
    is_configured = True
    if prov == "QWEN" and (not settings.qwen_api_key or not settings.qwen_api_key.strip()):
        is_configured = False

    return {
        "llm_provider": prov,
        "llm_model": model,
        "status": "configured" if is_configured else "missing_credentials",
    }


@router.post("/research", response_model=AIResearchResponseSchema)
async def conduct_ai_research(
    payload: AIResearchRequestSchema,
    session: AsyncSession = Depends(get_db),
):
    engine = ResearchAssistantEngine()
    result = await engine.conduct_research(
        query=payload.query,
        conversation_history=payload.history,
        subject_ticker=payload.subject_ticker,
    )

    # Persist immutable audit log record
    audit_entry = AIAuditLog(
        request_id=result["request_id"],
        provider=result["metadata"]["provider"],
        model=result["metadata"]["model"],
        prompt_version="research_v1",
        tools_invoked=[t["tool_name"] for t in result.get("tool_activity", [])],
        input_tokens=420,
        output_tokens=len(result["response"].split()),
        latency_ms=result["metadata"]["latency_ms"],
        estimated_cost_usd=0.0004,
        security_status="PASSED" if not result["metadata"]["is_adversarial_flagged"] else "FLAGGED_SANITIZED",
    )
    session.add(audit_entry)
    await session.commit()

    return result
