"""
AEGIS INVEST — LLM Provider Factory & Router
Dynamically routes to the configured LLM reasoning provider (AEGIS_INTERNAL_DETERMINISTIC, QWEN, etc.)
strictly adhering to environment configuration without silent fallbacks when explicit providers are selected.
"""

from typing import Optional
from app.ai.providers.base import LLMProvider
from app.ai.providers.demo_provider import DemoLLMProvider
from app.ai.providers.qwen import QwenLLMProvider
from app.core.config import get_settings
from app.core.errors import ConfigurationError
from app.core.logging import get_logger

logger = get_logger("aegis.ai.factory")

_provider_instance: Optional[LLMProvider] = None
_cached_config_key: Optional[tuple] = None


def get_llm_provider(
    provider_name: Optional[str] = None,
    model_name: Optional[str] = None,
    force_refresh: bool = False,
) -> LLMProvider:
    """
    Returns the active AI provider instance based on application configuration.
    
    Supported LLM_PROVIDER options:
    - AEGIS_INTERNAL_DETERMINISTIC (Default fallback, zero-external-dependency audited engine)
    - QWEN (Alibaba Cloud DashScope / OpenAI-compatible Qwen models, e.g. qwen3-32b, qwen3-8b, qwen-plus)
    """
    global _provider_instance, _cached_config_key
    settings = get_settings()

    target_provider = (provider_name or settings.llm_provider or "AEGIS_INTERNAL_DETERMINISTIC").strip().upper()
    target_model = model_name or settings.llm_model or ("qwen3-32b" if target_provider == "QWEN" else "aegis-institutional-v1")

    config_key = (target_provider, target_model, settings.qwen_api_key, settings.qwen_base_url)

    if _provider_instance is not None and not force_refresh and _cached_config_key == config_key:
        return _provider_instance

    logger.info(f"LLM provider selected: {target_provider} (model: '{target_model}')")

    if target_provider in {"AEGIS_INTERNAL_DETERMINISTIC", "DEMO", "INTERNAL"}:
        provider = DemoLLMProvider(model_name=target_model)
    elif target_provider == "QWEN":
        provider = QwenLLMProvider(
            api_key=settings.qwen_api_key,
            base_url=settings.qwen_base_url,
            model_name=target_model,
        )
    else:
        supported = ["AEGIS_INTERNAL_DETERMINISTIC", "QWEN"]
        raise ConfigurationError(
            f"Unsupported LLM_PROVIDER '{target_provider}'. Supported providers are: {', '.join(supported)}"
        )

    _provider_instance = provider
    _cached_config_key = config_key
    return provider


def reset_llm_provider() -> None:
    """Resets the cached provider singleton for test isolation or config reloading."""
    global _provider_instance, _cached_config_key
    _provider_instance = None
    _cached_config_key = None
