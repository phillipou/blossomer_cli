"""
llm_singleton.py - Shared LLM Client Instance

This module provides a singleton instance of the LLM client that should be used across
all services. It handles provider initialization, configuration, and ensures we only
have one instance of each provider.

Usage:
    from app.core.llm_singleton import get_llm_client

    async def my_service():
        client = get_llm_client()
        response = await client.generate(...)

Configuration:
    The following environment variables can be used to configure the LLM client:
    - LLM_PROVIDERS: Comma-separated list of enabled providers (default: "openai,anthropic,gemini")
    - LLM_CIRCUIT_BREAKER_DISABLE: Disable circuit breakers (default: false)
    - LLM_CIRCUIT_BREAKER_FAILURE_THRESHOLD: Number of failures before circuit opens (default: 5)
    - LLM_CIRCUIT_BREAKER_RECOVERY_TIMEOUT: Seconds before retry after circuit opens (default: 300)
"""

import os
from typing import Optional, List
from app.services.llm_service import (
    LLMClient,
    OpenAIProvider,
    AnthropicProvider,
    GeminiProvider,
    BaseLLMProvider,
)


# Global singleton instance
_llm_client: Optional[LLMClient] = None


def _get_enabled_providers() -> List[BaseLLMProvider]:
    """
    Get list of enabled LLM providers based on environment configuration.
    Providers are initialized in order of priority (lower number = higher priority).
    """
    enabled = os.getenv("LLM_PROVIDERS", "openai,anthropic,gemini").lower().split(",")
    providers: List[BaseLLMProvider] = []

    if "openai" in enabled:
        providers.append(OpenAIProvider())
    if "anthropic" in enabled:
        providers.append(AnthropicProvider())
    if "gemini" in enabled:
        providers.append(GeminiProvider())

    return providers


def get_llm_client(force_new: bool = False) -> LLMClient:
    """
    Get the shared LLM client instance. Creates a new instance if one doesn't exist
    or if force_new=True.

    Args:
        force_new: If True, creates a new instance even if one exists.
                  Useful for testing or when you need a clean instance.

    Returns:
        LLMClient: The shared LLM client instance
    """
    global _llm_client

    if _llm_client is None or force_new:
        providers = _get_enabled_providers()
        if not providers:
            raise RuntimeError(
                "No LLM providers enabled. Set LLM_PROVIDERS env var to enable providers."
            )
        _llm_client = LLMClient(providers)

    return _llm_client


# Initialize the default instance
llm_client = get_llm_client()
