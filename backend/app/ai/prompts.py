"""
AEGIS INVEST — Standard System Prompts & Structured Context Formatters
Establishes the epistemic and analytical constraints for external LLM reasoning layers (e.g. Qwen).
"""

from typing import Any, Dict, List, Optional
import json


AEGIS_SYSTEM_PROMPT = """You are AEGIS Invest's institutional financial intelligence reasoning layer.
You receive audited, verified structured financial data, valuation calculations, technical indicators, factor exposures, and risk analytics computed deterministically by AEGIS quantitative engines.

CORE DIRECTIVES:
1. Ground all analysis strictly on the supplied verified data.
2. NEVER fabricate, hallucinate, or extrapolate missing financial metrics, prices, or numbers.
3. Clearly distinguish empirical facts (from audited financial filings) from quantitative model outputs (DCF fair value, factor scores, risk metrics, scenario projections).
4. Explicitly state limitations, assumptions (such as WACC or terminal growth rates), and key invalidation conditions.
5. Explain uncertainty and downside risks plainly. Never provide guaranteed predictions, speculative hype, or certainty claims.
6. Maintain an institutional, objective, and evidence-linked tone.
"""


def build_structured_financial_context(
    ticker: str,
    company_profile: Optional[Dict[str, Any]] = None,
    fundamentals: Optional[Dict[str, Any]] = None,
    valuation: Optional[Dict[str, Any]] = None,
    technicals: Optional[Dict[str, Any]] = None,
    factors: Optional[Dict[str, Any]] = None,
    macro_regime: Optional[Dict[str, Any]] = None,
) -> str:
    """Formats structured quantitative engine outputs into an isolated JSON context block for the LLM."""
    payload: Dict[str, Any] = {
        "asset": {
            "symbol": ticker.upper(),
            "profile": company_profile or {},
        },
        "fundamentals": fundamentals or {},
        "valuation": valuation or {},
        "technicals": technicals or {},
        "technical": technicals or {},
        "factors": factors or {},
        "macro_regime": macro_regime or {},
    }
    return json.dumps(payload, indent=2, default=str)


def build_structured_portfolio_context(
    portfolio_name: str,
    holdings: List[Dict[str, Any]],
    analytics: Optional[Dict[str, Any]] = None,
    risk_profile: Optional[Dict[str, Any]] = None,
    stress_tests: Optional[List[Dict[str, Any]]] = None,
) -> str:
    """Formats structured portfolio, risk, and stress-test analytics for LLM reasoning."""
    payload: Dict[str, Any] = {
        "portfolio": {
            "name": portfolio_name,
            "holdings": holdings,
        },
        "performance_and_concentration": analytics or {},
        "risk_profile": risk_profile or {},
        "stress_test_scenarios": stress_tests or [],
    }
    return json.dumps(payload, indent=2, default=str)
