"""
AEGIS INVEST — Unit Tests for Qwen LLM Provider & Provider Router
Verifies provider selection, configuration validation, mocked API interactions,
tool calling, streaming, and error handling without external network dependencies.
"""

import json
from unittest.mock import AsyncMock, MagicMock, patch
import httpx
import pytest

from app.ai.prompts import AEGIS_SYSTEM_PROMPT, build_structured_financial_context
from app.ai.providers.base import LLMResponse, ToolCallRequest
from app.ai.providers.demo_provider import DemoLLMProvider
from app.ai.providers.factory import get_llm_provider, reset_llm_provider
from app.ai.providers.qwen import QwenLLMProvider
from app.core.config import get_settings
from app.core.errors import (
    ConfigurationError,
    LLMAuthenticationError,
    LLMProviderError,
    LLMRateLimitError,
)


@pytest.fixture(autouse=True)
def cleanup_provider_cache():
    """Ensure clean provider singleton cache for each test."""
    reset_llm_provider()
    yield
    reset_llm_provider()


def test_provider_router_selection_deterministic():
    """Verify selecting AEGIS_INTERNAL_DETERMINISTIC returns the deterministic provider."""
    provider = get_llm_provider("AEGIS_INTERNAL_DETERMINISTIC", model_name="aegis-institutional-v1", force_refresh=True)
    assert isinstance(provider, DemoLLMProvider)
    assert provider.model_name == "aegis-institutional-v1"
    assert provider.provider_name == "AEGIS_INTERNAL_DETERMINISTIC"


def test_provider_router_selection_qwen_valid():
    """Verify selecting QWEN with an API key returns QwenLLMProvider with configured model."""
    with patch("app.ai.providers.qwen.get_settings") as mock_settings:
        mock_settings.return_value = MagicMock(
            qwen_api_key="test-sk-qwen-12345",
            qwen_base_url="https://dashscope-intl.aliyuncs.com/compatible-mode/v1",
            llm_model="qwen3-32b",
            llm_provider="QWEN",
            llm_api_key=None,
        )
        provider = get_llm_provider("QWEN", model_name="qwen3-32b", force_refresh=True)
        assert isinstance(provider, QwenLLMProvider)
        assert provider.model_name == "qwen3-32b"
        assert provider.provider_name == "QWEN"


def test_provider_router_qwen_configurable_model():
    """Verify changing model from qwen3-32b to qwen3-8b or qwen-plus propagates without code changes."""
    provider_8b = QwenLLMProvider(
        api_key="mock-key",
        model_name="qwen3-8b",
    )
    assert provider_8b.model_name == "qwen3-8b"

    provider_plus = QwenLLMProvider(
        api_key="mock-key",
        model_name="qwen-plus",
    )
    assert provider_plus.model_name == "qwen-plus"


def test_provider_router_qwen_missing_api_key_raises():
    """Verify selecting QWEN without API credentials raises a clear ConfigurationError."""
    with patch("app.ai.providers.qwen.get_settings") as mock_settings:
        mock_settings.return_value = MagicMock(
            qwen_api_key=None,
            llm_api_key=None,
            qwen_base_url="https://dashscope-intl.aliyuncs.com/compatible-mode/v1",
            llm_model="qwen3-32b",
        )
        with pytest.raises(ConfigurationError) as exc_info:
            QwenLLMProvider(api_key=None)
        assert "Qwen API key is missing" in str(exc_info.value)


def test_provider_router_invalid_provider_raises():
    """Verify an unknown provider raises ConfigurationError listing supported choices."""
    with pytest.raises(ConfigurationError) as exc_info:
        get_llm_provider("UNKNOWN_LLM_PROVIDER", force_refresh=True)
    assert "Unsupported LLM_PROVIDER" in str(exc_info.value)
    assert "AEGIS_INTERNAL_DETERMINISTIC" in str(exc_info.value)
    assert "QWEN" in str(exc_info.value)


@pytest.mark.asyncio
async def test_qwen_provider_generate_success():
    """Verify successful Qwen generation and response normalization."""
    provider = QwenLLMProvider(api_key="test-key-mock", model_name="qwen3-32b")

    mock_qwen_response = {
        "id": "chatcmpl-qwen-123456",
        "object": "chat.completion",
        "created": 1710000000,
        "model": "qwen3-32b",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": "NVIDIA shows exceptional return on invested capital (>35%) and robust enterprise demand.",
                },
                "finish_reason": "stop",
            }
        ],
        "usage": {
            "prompt_tokens": 150,
            "completion_tokens": 25,
            "total_tokens": 175,
        },
    }

    mock_resp = MagicMock(status_code=200)
    mock_resp.json.return_value = mock_qwen_response

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_resp

        messages = [{"role": "user", "content": "Analyze NVIDIA fundamental positioning."}]
        res = await provider.generate(messages=messages, temperature=0.2, max_tokens=1000)

        assert isinstance(res, LLMResponse)
        assert "NVIDIA shows exceptional return" in res.content
        assert res.metadata is not None
        assert res.metadata.provider == "QWEN"
        assert res.metadata.model == "qwen3-32b"
        assert res.metadata.total_tokens == 175
        assert res.metadata.finish_reason == "stop"
        assert len(res.tool_calls) == 0

        # Verify system prompt was injected
        sent_payload = mock_post.call_args.kwargs["json"]
        assert sent_payload["model"] == "qwen3-32b"
        assert sent_payload["messages"][0]["role"] == "system"
        assert "AEGIS Invest" in sent_payload["messages"][0]["content"]


@pytest.mark.asyncio
async def test_qwen_provider_tool_calling():
    """Verify Qwen tool call requests are parsed into ToolCallRequest objects."""
    provider = QwenLLMProvider(api_key="test-key-mock", model_name="qwen3-32b")

    mock_tool_response = {
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": None,
                    "tool_calls": [
                        {
                            "id": "call_nvda_001",
                            "type": "function",
                            "function": {
                                "name": "get_valuation",
                                "arguments": json.dumps({"ticker": "NVDA"}),
                            },
                        }
                    ],
                },
                "finish_reason": "tool_calls",
            }
        ],
        "usage": {"prompt_tokens": 120, "completion_tokens": 20, "total_tokens": 140},
    }

    mock_resp = MagicMock(status_code=200)
    mock_resp.json.return_value = mock_tool_response

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_resp

        tools_def = [
            {
                "type": "function",
                "function": {
                    "name": "get_valuation",
                    "description": "Calculates DCF and multiples",
                    "parameters": {"type": "object", "properties": {"ticker": {"type": "string"}}},
                },
            }
        ]

        res = await provider.generate(
            messages=[{"role": "user", "content": "What is NVDA valuation?"}],
            tools=tools_def,
        )

        assert len(res.tool_calls) == 1
        assert res.tool_calls[0].tool_name == "get_valuation"
        assert res.tool_calls[0].arguments == {"ticker": "NVDA"}
        assert res.tool_calls[0].call_id == "call_nvda_001"


@pytest.mark.asyncio
async def test_qwen_provider_authentication_error():
    """Verify HTTP 401/403 triggers LLMAuthenticationError."""
    provider = QwenLLMProvider(api_key="invalid-key", model_name="qwen3-32b")

    mock_resp = MagicMock(status_code=401, text="Unauthorized: Invalid API key")
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_resp

        with pytest.raises(LLMAuthenticationError) as exc_info:
            await provider.generate([{"role": "user", "content": "Hello"}])
        assert "Qwen authentication rejected" in str(exc_info.value)


@pytest.mark.asyncio
async def test_qwen_provider_rate_limit_error():
    """Verify HTTP 429 triggers LLMRateLimitError."""
    provider = QwenLLMProvider(api_key="test-key", model_name="qwen3-32b")

    mock_resp = MagicMock(status_code=429, text="Too Many Requests")
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_resp

        with pytest.raises(LLMRateLimitError) as exc_info:
            await provider.generate([{"role": "user", "content": "Hello"}])
        assert "rate limit exceeded" in str(exc_info.value)


@pytest.mark.asyncio
async def test_qwen_provider_timeout_error():
    """Verify timeout triggers LLMProviderError with HTTP 504."""
    provider = QwenLLMProvider(api_key="test-key", model_name="qwen3-32b", timeout_seconds=2.0)

    with patch("httpx.AsyncClient.post", side_effect=httpx.TimeoutException("Read timed out")):
        with pytest.raises(LLMProviderError) as exc_info:
            await provider.generate([{"role": "user", "content": "Hello"}])
        assert "timed out" in str(exc_info.value)
        assert exc_info.value.status_code == 504


@pytest.mark.asyncio
async def test_qwen_provider_streaming():
    """Verify SSE streaming yields chunks until done."""
    provider = QwenLLMProvider(api_key="test-key", model_name="qwen3-32b")

    sse_lines = [
        'data: {"choices":[{"delta":{"content":"Institutional "}}]}',
        'data: {"choices":[{"delta":{"content":"research "}}]}',
        'data: {"choices":[{"delta":{"content":"summary."}}]}',
        "data: [DONE]",
    ]

    async def mock_aiter_lines():
        for line in sse_lines:
            yield line

    mock_response = MagicMock(status_code=200)
    mock_response.aiter_lines = mock_aiter_lines

    # Mock client.stream context manager
    mock_stream_ctx = AsyncMock()
    mock_stream_ctx.__aenter__.return_value = mock_response
    mock_stream_ctx.__aexit__.return_value = None

    with patch("httpx.AsyncClient.stream", return_value=mock_stream_ctx):
        chunks = []
        async for chunk in provider.stream([{"role": "user", "content": "Provide overview"}]):
            chunks.append(chunk)

        assert "".join(chunks) == "Institutional research summary."


def test_structured_context_builder():
    """Verify deterministic financial context formatter creates valid JSON context."""
    context_json = build_structured_financial_context(
        ticker="NVDA",
        company_profile={"name": "NVIDIA", "sector": "Technology"},
        fundamentals={"roic": 0.42, "sloan_accruals": 0.02},
        valuation={"pe_ratio": 45.2, "dcf_fair_value": 140.0},
        technicals={"trend": "BULLISH", "rsi": 62.5},
        factors={"quality_score": 92},
        macro_regime={"regime": "RISK_ON"},
    )

    parsed = json.loads(context_json)
    assert parsed["asset"]["symbol"] == "NVDA"
    assert parsed["fundamentals"]["roic"] == 0.42
    assert parsed["valuation"]["pe_ratio"] == 45.2
    assert parsed["technicals"]["rsi"] == 62.5
    assert parsed["macro_regime"]["regime"] == "RISK_ON"
