"""
AEGIS INVEST — Qwen LLM Provider
Production-grade integration for Qwen models via OpenAI-compatible endpoints (DashScope / custom inference servers).
Maintains strict deterministic financial calculations and formats structured reasoning.
"""

from datetime import datetime, timezone
import json
import time
from typing import Any, AsyncGenerator, Dict, List, Optional
import uuid
import httpx

from app.ai.prompts import AEGIS_SYSTEM_PROMPT
from app.ai.providers.base import LLMMetadata, LLMProvider, LLMResponse, ToolCallRequest
from app.core.config import get_settings
from app.core.errors import (
    ConfigurationError,
    LLMAuthenticationError,
    LLMProviderError,
    LLMRateLimitError,
)
from app.core.logging import get_logger

logger = get_logger("aegis.ai.qwen")


class QwenLLMProvider(LLMProvider):
    """Qwen AI reasoning provider implementing the unified LLMProvider interface."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model_name: Optional[str] = None,
        timeout_seconds: float = 30.0,
        max_retries: int = 2,
    ):
        settings = get_settings()
        self.api_key = api_key or settings.qwen_api_key or settings.llm_api_key
        if not self.api_key or not self.api_key.strip():
            raise ConfigurationError(
                "Qwen API key is missing. Set 'QWEN_API_KEY' in your environment or .env file to use LLM_PROVIDER=QWEN."
            )

        raw_base_url = (base_url or settings.qwen_base_url or "https://dashscope-intl.aliyuncs.com/compatible-mode/v1").rstrip("/")
        self.base_url = raw_base_url
        self.model_name = model_name or settings.llm_model or "qwen3-32b"
        self.timeout = timeout_seconds
        self.max_retries = max_retries
        self.provider_name = "QWEN"

        # Safe logging (never log the secret API key)
        logger.info(
            f"Initialized Qwen provider (model='{self.model_name}', endpoint='{self.base_url}')"
        )

    def _get_headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def _prepare_messages(self, messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Ensures AEGIS institutional system prompt is injected if not already present."""
        if not messages:
            return [{"role": "system", "content": AEGIS_SYSTEM_PROMPT}]

        prepared = list(messages)
        has_system = any(m.get("role") == "system" for m in prepared)
        if not has_system:
            prepared.insert(0, {"role": "system", "content": AEGIS_SYSTEM_PROMPT})
        return prepared

    async def generate(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.2,
        max_tokens: int = 2000,
        request_id: Optional[str] = None,
    ) -> LLMResponse:
        """Sends request to Qwen chat completions endpoint and returns normalized LLMResponse."""
        req_id = request_id or str(uuid.uuid4())
        start_time = time.perf_counter()

        endpoint = f"{self.base_url}/chat/completions"
        prepared_messages = self._prepare_messages(messages)

        payload: Dict[str, Any] = {
            "model": self.model_name,
            "messages": prepared_messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        # Convert tool format if provided
        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"

        logger.info(
            f"Qwen request started [{req_id}] (model='{self.model_name}', tools_count={len(tools) if tools else 0})"
        )

        response_data: Optional[Dict[str, Any]] = None
        last_exception: Optional[Exception] = None

        for attempt in range(self.max_retries + 1):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    resp = await client.post(
                        endpoint,
                        headers=self._get_headers(),
                        json=payload,
                    )

                if resp.status_code == 200:
                    try:
                        response_data = resp.json()
                        break
                    except Exception as json_err:
                        raise LLMProviderError(
                            f"Qwen returned malformed JSON response: {str(json_err)}",
                            provider=self.provider_name,
                            status_code=502,
                        )

                elif resp.status_code == 401 or resp.status_code == 403:
                    raise LLMAuthenticationError(
                        f"Qwen authentication rejected (HTTP {resp.status_code}). Verify QWEN_API_KEY.",
                        provider=self.provider_name,
                    )

                elif resp.status_code == 429:
                    raise LLMRateLimitError(
                        "Qwen API rate limit exceeded. Please retry after backoff.",
                        provider=self.provider_name,
                    )

                else:
                    err_text = resp.text[:300]
                    raise LLMProviderError(
                        f"Qwen API returned HTTP {resp.status_code}: {err_text}",
                        provider=self.provider_name,
                        status_code=resp.status_code if 400 <= resp.status_code <= 599 else 502,
                    )

            except (LLMAuthenticationError, LLMRateLimitError):
                raise
            except httpx.TimeoutException as tex:
                last_exception = LLMProviderError(
                    f"Qwen API request timed out after {self.timeout}s.",
                    provider=self.provider_name,
                    status_code=504,
                )
                logger.warning(f"Qwen request attempt {attempt + 1} timed out: {tex}")
            except httpx.RequestError as rex:
                last_exception = LLMProviderError(
                    f"Qwen API network connection failed: {str(rex)}",
                    provider=self.provider_name,
                    status_code=502,
                )
                logger.warning(f"Qwen request attempt {attempt + 1} failed: {rex}")
            except LLMProviderError as lpe:
                last_exception = lpe
                if attempt == self.max_retries:
                    raise
            except Exception as exc:
                last_exception = LLMProviderError(
                    f"Unexpected Qwen provider error: {str(exc)}",
                    provider=self.provider_name,
                    status_code=500,
                )
                logger.error(f"Unexpected Qwen error: {exc}")

        if response_data is None:
            if last_exception:
                raise last_exception
            raise LLMProviderError(
                "Qwen API returned empty response with no data.",
                provider=self.provider_name,
                status_code=502,
            )

        # Parse normalized output
        choices = response_data.get("choices", [])
        if not choices:
            raise LLMProviderError(
                "Qwen API response contained no choices.",
                provider=self.provider_name,
                status_code=502,
            )

        first_choice = choices[0]
        msg = first_choice.get("message", {})
        content = msg.get("content") or ""
        finish_reason = first_choice.get("finish_reason") or "stop"

        # Parse tool calls
        tool_calls: List[ToolCallRequest] = []
        raw_tool_calls = msg.get("tool_calls", [])
        if raw_tool_calls:
            for rtc in raw_tool_calls:
                call_id = rtc.get("id") or f"call_{uuid.uuid4().hex[:8]}"
                fn = rtc.get("function", {})
                tool_name = fn.get("name", "")
                raw_args = fn.get("arguments", "{}")
                if isinstance(raw_args, str):
                    try:
                        args = json.loads(raw_args)
                    except Exception:
                        args = {}
                elif isinstance(raw_args, dict):
                    args = raw_args
                else:
                    args = {}

                if tool_name:
                    tool_calls.append(ToolCallRequest(call_id=call_id, tool_name=tool_name, arguments=args))

        # Usage & latency
        latency = (time.perf_counter() - start_time) * 1000.0
        usage = response_data.get("usage", {})
        in_tokens = usage.get("prompt_tokens", 0)
        out_tokens = usage.get("completion_tokens", len(content.split()))
        total_tokens = usage.get("total_tokens", in_tokens + out_tokens)

        # Estimate standard Qwen token cost (approx $0.0008 / 1k tokens)
        cost_usd = round((total_tokens / 1000.0) * 0.0008, 6)

        logger.info(
            f"Qwen request completed [{req_id}] in {latency:.2f}ms (tokens={total_tokens}, finish_reason='{finish_reason}')"
        )

        return LLMResponse(
            content=content,
            tool_calls=tool_calls,
            metadata=LLMMetadata(
                provider=self.provider_name,
                model=self.model_name,
                request_id=req_id,
                latency_ms=round(latency, 2),
                input_tokens=in_tokens,
                output_tokens=out_tokens,
                total_tokens=total_tokens,
                estimated_cost_usd=cost_usd,
                finish_reason=finish_reason,
            ),
        )

    async def stream(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.2,
        max_tokens: int = 2000,
        request_id: Optional[str] = None,
    ) -> AsyncGenerator[str, None]:
        """Streams token chunks from Qwen using Server-Sent Events (SSE)."""
        req_id = request_id or str(uuid.uuid4())
        endpoint = f"{self.base_url}/chat/completions"
        prepared_messages = self._prepare_messages(messages)

        payload: Dict[str, Any] = {
            "model": self.model_name,
            "messages": prepared_messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": True,
        }
        if tools:
            payload["tools"] = tools

        logger.info(f"Qwen streaming started [{req_id}] (model='{self.model_name}')")

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                async with client.stream(
                    "POST",
                    endpoint,
                    headers=self._get_headers(),
                    json=payload,
                ) as response:
                    if response.status_code != 200:
                        err_body = await response.aread()
                        raise LLMProviderError(
                            f"Qwen stream failed with HTTP {response.status_code}: {err_body.decode('utf-8', errors='ignore')[:200]}",
                            provider=self.provider_name,
                            status_code=response.status_code,
                        )

                    async for line in response.aiter_lines():
                        if not line:
                            continue
                        line_str = line.strip()
                        if line_str.startswith("data:"):
                            chunk_data = line_str[5:].strip()
                            if chunk_data == "[DONE]":
                                break
                            try:
                                parsed = json.loads(chunk_data)
                                choices = parsed.get("choices", [])
                                if choices:
                                    delta = choices[0].get("delta", {})
                                    chunk_text = delta.get("content")
                                    if chunk_text:
                                        yield chunk_text
                            except Exception:
                                continue
        except Exception as exc:
            logger.error(f"Error during Qwen stream: {exc}")
            raise LLMProviderError(f"Qwen stream error: {str(exc)}", provider=self.provider_name)
