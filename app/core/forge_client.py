"""
forge_client.py - TensorBlock Forge Unified LLM Client

This module provides a unified interface to access multiple LLM providers through
TensorBlock Forge, which abstracts away provider-specific implementations and provides
a single OpenAI-compatible API for all major LLM providers.

Key Benefits:
- Single API key for all providers (FORGE_API_KEY)
- OpenAI-compatible interface for easy integration
- Model switching via runtime parameters
- Cost optimization through provider comparison
- Future-proof with automatic new provider support

Usage:
    from app.core.forge_client import get_forge_client
    
    forge_client = get_forge_client()
    response = await forge_client.chat_completion(
        messages=[{"role": "user", "content": "Hello"}],
        model="gemini-1.5-flash"
    )

Supported Models:
- OpenAI: gpt-4o, gpt-4o-mini, gpt-3.5-turbo
- Anthropic: claude-3-5-sonnet, claude-3-5-haiku, claude-3-opus  
- Google: gemini-1.5-pro, gemini-1.5-flash, gemini-2.0-flash
- And more via TensorBlock Forge
"""

import os
import logging
from typing import Optional, Dict, Any, List
import openai
from openai.types.chat import ChatCompletion

# Load environment variables from .env file if available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv not available, use system environment


class ForgeClient:
    """
    Unified LLM client using TensorBlock Forge infrastructure.
    
    Provides OpenAI-compatible interface for all major LLM providers.
    """
    
    def __init__(self, api_key: Optional[str] = None, base_url: str = "https://api.forge.tensorblock.co/v1"):
        """
        Initialize the Forge client.
        
        Args:
            api_key: TensorBlock Forge API key. If None, reads from FORGE_API_KEY env var.
            base_url: TensorBlock Forge API base URL. Correct endpoint: "https://api.forge.tensorblock.co/v1"
        """
        self.api_key = api_key or os.getenv("FORGE_API_KEY")
        if not self.api_key:
            raise ValueError(
                "FORGE_API_KEY environment variable not set. "
                "Get your API key from https://tensorblock.co"
            )
        
        self.client = openai.OpenAI(
            api_key=self.api_key,
            base_url=base_url
        )
        
        # Model cost mapping with correct TensorBlock model IDs (approximate costs per 1K tokens)
        self.model_costs = {
            # OpenAI models (via TensorBlock)
            "OpenAI/gpt-4o": {"input": 0.005, "output": 0.015},
            "OpenAI/gpt-4o-mini": {"input": 0.00015, "output": 0.0006},
            "OpenAI/gpt-4.1-nano": {"input": 0.000015, "output": 0.00006},  # Ultra cheap and fast
            "OpenAI/gpt-3.5-turbo": {"input": 0.001, "output": 0.002},
            "OpenAI/gpt-4.1-nano": {"input": 0.0001, "output": 0.0004},  # Very cost-effective
            "OpenAI/gpt-4.1-mini": {"input": 0.0002, "output": 0.0008},
            "OpenAI/gpt-4.1": {"input": 0.003, "output": 0.012},
            
            # Anthropic models (via TensorBlock) 
            "Anthropic/claude-3-5-sonnet-20241022": {"input": 0.003, "output": 0.015},
            "Anthropic/claude-3-5-haiku-20241022": {"input": 0.00025, "output": 0.00125},
            "Anthropic/claude-3-opus-20240229": {"input": 0.015, "output": 0.075},
            "Anthropic/claude-sonnet-4-20250514": {"input": 0.003, "output": 0.015},  # Latest Sonnet
            
            # Gemini models (via TensorBlock)
            "Gemini/models/gemini-1.5-pro": {"input": 0.00125, "output": 0.005},
            "Gemini/models/gemini-1.5-flash": {"input": 0.000075, "output": 0.0003},
            "Gemini/models/gemini-2.0-flash": {"input": 0.000075, "output": 0.0003},
            "Gemini/models/gemini-2.5-flash": {"input": 0.000075, "output": 0.0003},  # Latest Flash
            "Gemini/models/gemini-2.5-pro": {"input": 0.00125, "output": 0.005},     # Latest Pro
            "Gemini/models/gemini-1.5-flash-8b": {"input": 0.0000375, "output": 0.00015},  # Ultra cheap
            
            # xAI models (via TensorBlock)
            "xAI/grok-3-mini": {"input": 0.0002, "output": 0.0008},      # Fast and cheap
            "xAI/grok-3": {"input": 0.002, "output": 0.008},             # High quality
            
            # Deepseek models (via TensorBlock)
            "Deepseek/deepseek-chat": {"input": 0.0001, "output": 0.0002},  # Very cost-effective
        }
        
        logging.info(f"Initialized Forge client with base URL: {base_url}")
    
    async def chat_completion(
        self, 
        messages: List[Dict[str, str]], 
        model: str,
        **kwargs
    ) -> ChatCompletion:
        """
        Generate chat completion using specified model.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content' keys
            model: Model name (e.g., "gemini-1.5-flash", "claude-3-5-haiku")
            **kwargs: Additional parameters (temperature, max_tokens, etc.)
            
        Returns:
            OpenAI ChatCompletion response object
            
        Raises:
            Exception: On API errors or invalid model names
        """
        try:
            import asyncio
            
            # Log the model being used for debugging
            cost_info = self.model_costs.get(model, {"input": "unknown", "output": "unknown"})
            logging.info(f"Using model: {model} (cost: ~${cost_info['input']}/1K input tokens)")
            
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.client.chat.completions.create(
                    model=model,
                    messages=messages,
                    **kwargs
                )
            )
            
            return response
            
        except Exception as e:
            logging.error(f"Forge client error for model {model}: {e}")
            raise
    
    def get_cost_estimate(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """
        Estimate cost for a given model and token usage.
        
        Args:
            model: Model name
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            
        Returns:
            Estimated cost in USD
        """
        if model not in self.model_costs:
            logging.warning(f"Unknown model for cost estimation: {model}")
            return 0.0
        
        costs = self.model_costs[model]
        input_cost = (input_tokens / 1000) * costs["input"]
        output_cost = (output_tokens / 1000) * costs["output"]
        
        return input_cost + output_cost
    
    def list_available_models(self) -> List[str]:
        """
        Get list of available models.
        
        Returns:
            List of model names
        """
        return list(self.model_costs.keys())
    
    def get_recommended_model(self, use_case: str = "general") -> str:
        """
        Get recommended model for specific use case.
        
        Args:
            use_case: Use case type ("fast", "quality", "cost", "general")
            
        Returns:
            Recommended model name
        """
        # Updated with actual TensorBlock model IDs
        recommendations = {
            "fast": "Gemini/models/gemini-1.5-flash-8b",     # Ultra fast and cheapest
            "cost": "Deepseek/deepseek-chat",                # Most cost-effective
            "quality": "Anthropic/claude-sonnet-4-20250514", # Highest quality (latest Claude)
            "general": "OpenAI/gpt-4.1-nano",                 # Best balance - very cheap and capable
            "coding": "Deepseek/deepseek-chat",              # Great for code
            "reasoning": "OpenAI/gpt-4.1-nano",             # Good reasoning, very cheap
        }
        
        return recommendations.get(use_case, "OpenAI/gpt-4.1-nano")


# Global singleton instance
_forge_client: Optional[ForgeClient] = None


def get_forge_client(force_new: bool = False) -> ForgeClient:
    """
    Get the shared Forge client instance.
    
    Args:
        force_new: If True, creates a new instance even if one exists
        
    Returns:
        ForgeClient instance
    """
    global _forge_client
    
    if _forge_client is None or force_new:
        _forge_client = ForgeClient()
    
    return _forge_client


# Initialize default instance for backward compatibility (lazy loading)
forge_client = None