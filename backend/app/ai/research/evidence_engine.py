"""
AEGIS INVEST — Evidence Engine
Extracts normalized, auditable evidence units from quantitative engine results,
classifying each into FACT, CALCULATION, MODEL_OUTPUT, SCENARIO, or UNCERTAINTY.
"""

import hashlib
import json
from typing import Any, Dict, List, Optional
import uuid


class EvidenceEngine:
    """Institutional evidence extraction and citation attribution engine."""

    def extract_evidence_from_tool_results(
        self,
        tool_name: str,
        tool_output: Dict[str, Any],
        subject_id: str,
    ) -> List[Dict[str, Any]]:
        """
        Converts raw deterministic tool data into structured, traceable evidence records.
        """
        evidence_items: List[Dict[str, Any]] = []

        if tool_name == "get_fundamentals":
            growths = tool_output.get("growth_metrics", {})
            profits = tool_output.get("profitability_metrics", {})
            
            if "revenue_growth_yoy" in growths and growths["revenue_growth_yoy"] is not None:
                evidence_items.append(self._create_item(
                    source_type="FINANCIAL_STATEMENT",
                    source_id=f"{subject_id}_INCOME_STMT",
                    source_name=f"{subject_id} Audited Financials",
                    metric="Revenue Growth (YoY)",
                    value=f"{growths['revenue_growth_yoy'] * 100.0:.1f}%",
                    category="FACT",
                ))
            if "operating_margin" in profits and profits["operating_margin"] is not None:
                evidence_items.append(self._create_item(
                    source_type="FINANCIAL_STATEMENT",
                    source_id=f"{subject_id}_INCOME_STMT",
                    source_name=f"{subject_id} Audited Financials",
                    metric="Operating Margin",
                    value=f"{profits['operating_margin'] * 100.0:.1f}%",
                    category="CALCULATION",
                ))

        elif tool_name == "get_valuation":
            multiples = tool_output.get("multiples", {})
            dcf = tool_output.get("dcf", {})
            if "pe_ratio" in multiples and multiples["pe_ratio"] is not None:
                evidence_items.append(self._create_item(
                    source_type="VALUATION_ENGINE",
                    source_id=f"{subject_id}_MULTIPLES",
                    source_name="Aegis Valuation Multiples Engine",
                    metric="Trailing P/E Ratio",
                    value=f"{multiples['pe_ratio']:.1f}x",
                    category="CALCULATION",
                ))
            if "fair_value_per_share" in dcf:
                evidence_items.append(self._create_item(
                    source_type="VALUATION_ENGINE",
                    source_id=f"{subject_id}_DCF",
                    source_name="Aegis Discounted Cash Flow Model",
                    metric="DCF Fair Value Estimate",
                    value=f"${dcf['fair_value_per_share']:.2f}",
                    category="MODEL_OUTPUT",
                ))

        elif tool_name == "get_market_regime":
            regime = tool_output.get("current_regime", "BULL_TREND")
            evidence_items.append(self._create_item(
                source_type="REGIME_ENGINE",
                source_id="MARKET_REGIME_LATEST",
                source_name="Aegis Market Regime Detection Engine",
                metric="Current Market Regime",
                value=str(regime),
                category="MODEL_OUTPUT",
            ))

        elif tool_name == "get_factor_exposure":
            scorecard = tool_output.get("factor_scores", {})
            for factor, score in scorecard.items():
                evidence_items.append(self._create_item(
                    source_type="FACTOR_ENGINE",
                    source_id=f"{subject_id}_FACTORS",
                    source_name="Aegis Quantitative Factor Model",
                    metric=f"{factor.capitalize()} Factor Score",
                    value=f"{score:.2f} / 10.0",
                    category="CALCULATION",
                ))

        return evidence_items

    def _create_item(
        self,
        source_type: str,
        source_id: str,
        source_name: str,
        metric: str,
        value: str,
        category: str,
        period: Optional[str] = "LTM",
        confidence: float = 0.95,
    ) -> Dict[str, Any]:
        raw_str = f"{source_type}|{source_id}|{metric}|{value}"
        p_hash = hashlib.sha256(raw_str.encode("utf-8")).hexdigest()
        return {
            "id": f"ev_{uuid.uuid4().hex[:8]}",
            "source_type": source_type,
            "source_id": source_id,
            "source_name": source_name,
            "metric": metric,
            "value": value,
            "period": period,
            "confidence": confidence,
            "category": category,
            "provenance_hash": p_hash,
        }
