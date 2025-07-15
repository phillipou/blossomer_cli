"""
CLI-adapted LLM Singleton - Removes web dependencies
"""

import os
from typing import Optional, List
from cli.services.llm_service import LLMClient, OpenAIProvider, BaseLLMProvider

# Global singleton instance
_llm_client: Optional[LLMClient] = None


def _get_enabled_providers() -> List[BaseLLMProvider]:
    """Get list of enabled LLM providers based on environment configuration."""
    enabled = os.getenv("LLM_PROVIDERS", "openai").lower().split(",")
    providers: List[BaseLLMProvider] = []

    if "openai" in enabled:
        providers.append(OpenAIProvider())
    
    # Note: Only OpenAI is implemented for CLI context
    # Add other providers here when needed

    return providers


def get_llm_client(force_new: bool = False) -> LLMClient:
    """Get the shared LLM client instance."""
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