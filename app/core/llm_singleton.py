"""
llm_singleton.py - Shared LLM Client Instance (Forge-based)

This module provides a singleton instance of the Forge LLM service that should be used across
all services. It uses TensorBlock Forge for unified access to multiple LLM providers.

MIGRATION NOTE: This module has been updated to use TensorBlock Forge instead of 
individual provider implementations. The new system provides:
- Single API key (FORGE_API_KEY) for all providers
- Model switching via parameters
- Cost optimization through provider comparison
- Simplified error handling

Usage:
    from app.core.llm_singleton import get_llm_client

    async def my_service():
        client = get_llm_client()
        response = await client.generate(...)

Configuration:
    Environment variables:
    - FORGE_API_KEY: TensorBlock Forge API key (recommended)
    - OPENAI_API_KEY: Legacy OpenAI key (fallback)
    - GTM_CLI_DEFAULT_MODEL: Default model to use (default: gpt-4o-mini)
"""

import os
import logging
from typing import Optional
from app.core.forge_llm_service import get_forge_llm_service, ForgeLLMService


# Global singleton instance  
_llm_client: Optional[ForgeLLMService] = None


def get_llm_client(force_new: bool = False, default_model: str = None) -> ForgeLLMService:
    """
    Get the shared Forge LLM service instance. Creates a new instance if one doesn't exist
    or if force_new=True.

    Args:
        force_new: If True, creates a new instance even if one exists.
                  Useful for testing or when you need a clean instance.
        default_model: Default model to use. If None, uses environment variable or "gpt-4o-mini"

    Returns:
        ForgeLLMService: The shared Forge LLM service instance
    """
    global _llm_client

    if _llm_client is None or force_new:
        # Get default model from environment or use provided default
        if default_model is None:
            default_model = os.getenv("GTM_CLI_DEFAULT_MODEL", "OpenAI/gpt-4.1-nano")
        
        _llm_client = get_forge_llm_service(default_model=default_model)
        logging.info(f"Initialized LLM client with default model: {default_model}")

    return _llm_client


def set_default_model(model: str):
    """
    Set the default model for the LLM client.
    
    Args:
        model: Model name to set as default
    """
    client = get_llm_client()
    client.set_default_model(model)


def get_available_models():
    """Get list of available models from the LLM client."""
    client = get_llm_client()
    return client.get_available_models()


def get_recommended_model(use_case: str = "general") -> str:
    """
    Get recommended model for a specific use case.
    
    Args:
        use_case: Use case type ("fast", "quality", "cost", "general")
        
    Returns:
        Recommended model name
    """
    client = get_llm_client()
    return client.get_recommended_model(use_case)


# Initialize the default instance
llm_client = get_llm_client()


# Backward compatibility aliases
LLMClient = ForgeLLMService  # For code that imports LLMClient directly
