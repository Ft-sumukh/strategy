"""
AEGIS INVEST — AI Safety, Guardrails & Anti-Prompt-Injection Defenses
Treats all external texts, news headlines, and user prompts as untrusted input.
Enforces strict epistemic uncertainty boundaries (blocks certainty/prediction fallacies).
"""

import re
from typing import Dict, List, Tuple


# Regex patterns of known adversarial prompt injections
INJECTION_PATTERNS = [
    r"(?i)ignore\s+(all\s+)?(previous|prior)\s+instructions",
    r"(?i)system\s+prompt\s+override",
    r"(?i)reveal\s+(the\s+)?(system\s+prompt|api\s+key|password|secret)",
    r"(?i)drop\s+table",
    r"(?i)delete\s+from",
    r"(?i)execute\s+(sql|command|script)",
    r"(?i)you\s+are\s+now\s+dan",
    r"(?i)jailbreak",
]

# Epistemic certainty violations and their evidence-based replacements
CERTAINTY_REPLACEMENTS = [
    (r"(?i)\bguaranteed\b", "empirically observed"),
    (r"(?i)\brisk-free\b", "lower-volatility"),
    (r"(?i)\bwill\s+definitely\s+rise\b", "shows historical positive momentum"),
    (r"(?i)\bwill\s+definitely\s+fall\b", "shows historical downside sensitivity"),
    (r"(?i)\bcannot\s+lose\b", "has historically exhibited downside mitigation"),
    (r"(?i)\b100%\s+certain\b", "strongly supported by current data"),
]


class AISafetyGuardrail:
    """Security and epistemic safety guardrail for AI reasoning."""

    @staticmethod
    def sanitize_untrusted_input(text: str) -> Tuple[str, bool]:
        """
        Sanitizes user queries and external news text against prompt injections.
        Returns (sanitized_text, is_flagged).
        """
        if not text:
            return "", False

        is_flagged = False
        clean_text = text

        for pattern in INJECTION_PATTERNS:
            if re.search(pattern, clean_text):
                is_flagged = True
                clean_text = re.sub(pattern, "[FILTERED_ADVERSARIAL_INPUT]", clean_text)

        # Enforce max character limit to prevent token flood attacks
        if len(clean_text) > 8000:
            clean_text = clean_text[:8000]

        return clean_text, is_flagged

    @staticmethod
    def enforce_epistemic_safety(text: str) -> str:
        """
        Replaces absolute certainty/prediction claims with evidence-based expressions.
        """
        if not text:
            return ""

        output = text
        for pattern, replacement in CERTAINTY_REPLACEMENTS:
            output = re.sub(pattern, replacement, output)

        return output
