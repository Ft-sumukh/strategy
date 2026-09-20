"""
AEGIS INVEST — Provider-Agnostic LLM Abstraction
Defines the base interface, structured response schemas, token usage metrics,
and metadata requirements for all AI reasoning providers.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, AsyncGenerator, Dict, List, Optional


@dataclass
class ToolCallRequest:
    """Tool execution request emitted by the LLM."""
    call_id: str
    tool_name: str
    arguments: Dict[str, Any]


@dataclass
class LLMMetadata:
    """Standardized institutional execution metadata for AI observability."""
    provider: str
    model: str
    request_id: str
    latency_ms: float
    input_tokens: int
    output_tokens: int
    total_tokens: int
    estimated_cost_usd: float
    finish_reason: str
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class LLMResponse:
    """Normalized structured response from an AI reasoning provider."""
    content: str
    tool_calls: List[ToolCallRequest] = field(default_factory=list)
    metadata: Optional[LLMMetadata] = None
    citations: List[Dict[str, Any]] = field(default_factory=list)
    uncertainty_statement: Optional[str] = None


class LLMProvider(ABC):
    """Abstract interface for multi-provider AI reasoning (Demo, OpenAI, Gemini, Claude)."""

    @abstractmethod
    async def generate(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.2,
        max_tokens: int = 2000,
        request_id: Optional[str] = None,
    ) -> LLMResponse:
        """Generates a structured LLM response with optional tool calls."""
        pass

    @abstractmethod
    async def stream(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.2,
        max_tokens: int = 2000,
        request_id: Optional[str] = None,
    ) -> AsyncGenerator[str, None]:
        """Streams token chunks for interactive research workspaces."""
        pass

    async def generate_prompt(
        self,
        system_prompt: str,
        user_prompt: str,
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.2,
        max_tokens: int = 2000,
        request_id: Optional[str] = None,
    ) -> LLMResponse:
        """Convenience method accepting system and user prompts directly."""
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
        return await self.generate(
            messages=messages,
            tools=tools,
            temperature=temperature,
            max_tokens=max_tokens,
            request_id=request_id,
        )
