"""
AEGIS INVEST — AI Research Assistant Engine
Coordinates query intent detection, controlled tool execution, evidence synthesis,
and citation attribution while enforcing anti-prompt-injection defenses and epistemic bounds.
"""

from datetime import datetime, timezone
import json
import time
from typing import Any, Dict, List, Optional
import uuid

from app.ai.guardrails.safety import AISafetyGuardrail
from app.ai.providers.factory import get_llm_provider
from app.ai.research.evidence_engine import EvidenceEngine
from app.ai.tools.registry import ToolRegistry


class ResearchAssistantEngine:
    """Institutional investment research assistant engine."""

    def __init__(self):
        self.provider = get_llm_provider()
        self.tool_registry = ToolRegistry()
        self.evidence_engine = EvidenceEngine()

    async def conduct_research(
        self,
        query: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        subject_ticker: Optional[str] = None,
        user_id: str = "default_user",
    ) -> Dict[str, Any]:
        """
        Full evidence-backed research workflow:
        Query -> Sanitization -> Tool Execution -> Evidence Collection -> Synthesis -> Citations.
        """
        req_id = str(uuid.uuid4())
        start_time = time.perf_counter()

        # 1. Guardrail input query
        clean_query, is_flagged = AISafetyGuardrail.sanitize_untrusted_input(query)

        # 2. Assemble prompt message history
        messages: List[Dict[str, str]] = []
        if conversation_history:
            messages.extend(conversation_history)
        messages.append({"role": "user", "content": clean_query})

        # 3. First LLM turn with tool registry
        tools_def = self.tool_registry.list_tools()
        first_resp = await self.provider.generate(
            messages=messages,
            tools=tools_def,
            request_id=req_id,
        )

        executed_tools_log: List[Dict[str, Any]] = []
        collected_evidence: List[Dict[str, Any]] = []

        # 4. Execute tool calls if requested
        if first_resp.tool_calls:
            for tc in first_resp.tool_calls:
                t_res = await self.tool_registry.execute_tool(tc.tool_name, tc.arguments)
                executed_tools_log.append({
                    "call_id": tc.call_id,
                    "tool_name": tc.tool_name,
                    "arguments": tc.arguments,
                    "status": t_res.get("status", "SUCCESS"),
                    "latency_ms": t_res.get("latency_ms", 0.0),
                })

                # Extract normalized evidence from output
                ticker_sub = tc.arguments.get("ticker", subject_ticker or "PORTFOLIO")
                if t_res.get("status") == "SUCCESS" and "data" in t_res:
                    ev_items = self.evidence_engine.extract_evidence_from_tool_results(
                        tc.tool_name, t_res["data"], str(ticker_sub)
                    )
                    collected_evidence.extend(ev_items)

            # Pass tool outputs and verified calculations back to LLM for synthesis turn
            tool_data_summary = json.dumps(
                [
                    {
                        "tool": t["tool_name"],
                        "arguments": t["arguments"],
                        "status": t["status"],
                        "extracted_evidence": [
                            {"metric": e.get("metric"), "value": e.get("value"), "category": e.get("category")}
                            for e in collected_evidence
                        ],
                    }
                    for t in executed_tools_log
                ],
                indent=2,
                default=str,
            )
            messages.append({"role": "assistant", "content": "I am gathering data from analytical engines."})
            messages.append({
                "role": "tool",
                "content": f"Analytical engines responded with verified data:\n{tool_data_summary}",
            })

            # Final synthesis turn
            final_resp = await self.provider.generate(
                messages=messages,
                tools=None,
                request_id=req_id,
            )
        else:
            final_resp = first_resp

        # 5. Apply epistemic safety guardrail on output
        safe_content = AISafetyGuardrail.enforce_epistemic_safety(final_resp.content)
        total_latency = (time.perf_counter() - start_time) * 1000.0

        citations = final_resp.citations or [
            {
                "id": ev["id"],
                "source_type": ev["source_type"],
                "source_name": ev["source_name"],
                "metric": ev["metric"],
                "value": ev["value"],
                "category": ev["category"],
            }
            for ev in collected_evidence[:6]
        ]

        return {
            "request_id": req_id,
            "response": safe_content,
            "citations": citations,
            "evidence": collected_evidence,
            "tool_activity": executed_tools_log,
            "uncertainty_statement": final_resp.uncertainty_statement or (
                "Valuation, factor, and stress scenario estimates reflect mathematical models and historical distributions. "
                "Unanticipated macro or competitive shocks could alter actual future financial trajectories."
            ),
            "metadata": {
                "model": final_resp.metadata.model if final_resp.metadata else "aegis-institutional-v1",
                "provider": final_resp.metadata.provider if final_resp.metadata else "AEGIS_INTERNAL_DETERMINISTIC",
                "latency_ms": round(total_latency, 2),
                "tools_executed_count": len(executed_tools_log),
                "is_adversarial_flagged": is_flagged,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        }
