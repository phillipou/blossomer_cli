"""
CLI-adapted LLM Singleton - Uses TensorBlock Forge for unified access

MIGRATION NOTE: Updated to use TensorBlock Forge instead of individual providers.
This provides unified access to multiple LLM providers through a single API key.
"""

import os
import logging
from typing import Optional
from app.core.forge_llm_service import get_forge_llm_service, ForgeLLMService

# Global singleton instance
_llm_client: Optional[ForgeLLMService] = None


def get_llm_client(force_new: bool = False, default_model: str = None) -> ForgeLLMService:
    """
    Get the shared Forge LLM service instance for CLI context.
    
    Args:
        force_new: If True, creates a new instance even if one exists
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
        logging.info(f"Initialized CLI LLM client with default model: {default_model}")

    return _llm_client


def set_default_model(model: str):
    """Set the default model for the CLI LLM client."""
    client = get_llm_client()
    client.set_default_model(model)


def get_available_models():
    """Get list of available models from the CLI LLM client."""
    client = get_llm_client()
    return client.get_available_models()


# Initialize the default instance
llm_client = get_llm_client()

# Backward compatibility aliases
from cli.services.llm_service import LLMClient as LegacyLLMClient
LLMClient = ForgeLLMService  # For code that imports LLMClient directly