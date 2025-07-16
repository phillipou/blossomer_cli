"""
forge_llm_service.py - Simplified LLM Service using TensorBlock Forge

This module provides a simplified LLM service that uses TensorBlock Forge
for unified access to multiple LLM providers. It replaces the complex
provider-specific implementations with a single, clean interface.

Key benefits:
- Single API key for all providers
- Model switching via parameters
- Unified error handling
- Cost tracking
- Simple implementation
"""

import logging
import json
import asyncio
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, ValidationError

from app.core.forge_client import get_forge_client, ForgeClient
import os


class LLMRequest(BaseModel):
    """Standardized input model for LLM requests."""
    
    system_prompt: Optional[str] = None
    user_prompt: str
    parameters: Optional[Dict[str, Any]] = None
    response_schema: Optional[Dict[str, Any]] = None
    model: Optional[str] = None  # Model to use for this request

    @property
    def prompt(self) -> str:
        """Combine system and user prompts for backward compatibility."""
        if self.system_prompt:
            return f"{self.system_prompt}\n\n{self.user_prompt}"
        return self.user_prompt


class LLMResponse(BaseModel):
    """Standardized output model for LLM responses."""
    
    text: str
    model: Optional[str] = None
    usage: Optional[Dict[str, Any]] = None
    provider: Optional[str] = None
    cost_estimate: Optional[float] = None


class CLIException(Exception):
    """CLI-specific exception to replace HTTPException"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.details = details or {}
        super().__init__(message)


class ForgeLLMService:
    """
    Simplified LLM service using TensorBlock Forge.
    
    Replaces complex provider management with unified Forge access.
    """
    
    def __init__(self, default_model: str = "OpenAI/gpt-4.1-nano"):
        """
        Initialize the Forge LLM service.
        
        Args:
            default_model: Default model to use when none is specified
        """
        self.default_model = default_model
        self.forge_client: Optional[ForgeClient] = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the Forge client with API key checking."""
        try:
            # Check if we have a Forge API key
            forge_key = os.getenv("FORGE_API_KEY")
            openai_key = os.getenv("OPENAI_API_KEY")
            
            if forge_key:
                self.forge_client = get_forge_client()
                logging.info("Initialized Forge LLM service with unified API access")
            elif openai_key:
                logging.warning(
                    "Using legacy OpenAI API key. Consider migrating to FORGE_API_KEY "
                    "for access to multiple providers (Gemini, Claude, GPT)"
                )
                # We'll still use Forge client but with OpenAI key
                self.forge_client = get_forge_client()
            else:
                raise CLIException(
                    "No API key available. Set FORGE_API_KEY or OPENAI_API_KEY environment variable."
                )
                    
        except Exception as e:
            logging.error(f"Failed to initialize Forge client: {e}")
            self.forge_client = None
    
    def _ensure_client(self):
        """Ensure the Forge client is available."""
        if not self.forge_client:
            raise CLIException(
                "Forge client not initialized. Check your API key configuration."
            )
    
    async def generate(self, request: LLMRequest) -> LLMResponse:
        """
        Generate a response using the specified or default model.
        
        Args:
            request: LLM request with prompt and optional model
            
        Returns:
            LLM response with text and metadata
            
        Raises:
            CLIException: On API errors or configuration issues
        """
        self._ensure_client()
        
        try:
            # Determine model to use
            model = request.model or self.default_model
            
            # Prepare parameters
            kwargs = request.parameters.copy() if request.parameters else {}
            
            # Handle structured output
            if request.response_schema:
                kwargs["response_format"] = {"type": "json_object"}
            
            # Build messages
            messages = []
            if request.system_prompt:
                messages.append({"role": "system", "content": request.system_prompt})
            
            user_content = request.user_prompt
            if request.response_schema and "json" not in user_content.lower():
                user_content += "\n\nRespond with ONLY valid JSON. No other text or formatting."
            messages.append({"role": "user", "content": user_content})
            
            # Log model usage for debugging
            logging.info(f"Using model: {model}")
            
            # Make API call
            response = await self.forge_client.chat_completion(
                messages=messages,
                model=model,
                **kwargs
            )
            
            # Extract response data
            text = response.choices[0].message.content if response.choices else ""
            usage = dict(response.usage) if hasattr(response, "usage") else None
            
            # Calculate cost estimate
            cost_estimate = None
            if usage and "prompt_tokens" in usage and "completion_tokens" in usage:
                cost_estimate = self.forge_client.get_cost_estimate(
                    model=model,
                    input_tokens=usage["prompt_tokens"],
                    output_tokens=usage["completion_tokens"]
                )
            
            return LLMResponse(
                text=text,
                model=model,
                provider="forge",
                usage=usage,
                cost_estimate=cost_estimate
            )
            
        except Exception as e:
            logging.error(f"Forge LLM service error: {e}", exc_info=True)
            raise CLIException(f"LLM generation failed: {str(e)}")
    
    async def generate_structured_output(
        self,
        prompt: str,
        response_model: type[BaseModel],
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
    ) -> BaseModel:
        """
        Generate structured output and validate against a Pydantic model.
        
        Args:
            prompt: User prompt
            response_model: Pydantic model for validation
            system_prompt: Optional system prompt
            model: Optional model override
            
        Returns:
            Validated Pydantic model instance
            
        Raises:
            CLIException: On validation or API errors
        """
        try:
            # Create request with JSON schema
            json_system_prompt = "You are a helpful assistant that responds with valid JSON only. Never include any text outside the JSON response."
            if system_prompt:
                json_system_prompt = f"{system_prompt}\n\nIMPORTANT: Respond with valid JSON only. No additional text or formatting."
            
            request = LLMRequest(
                user_prompt=f"{prompt}\n\nRespond with valid JSON matching this schema: {response_model.model_json_schema()}",
                system_prompt=json_system_prompt,
                model=model or self.default_model,
                parameters={"temperature": 0.1},  # Low temperature for structured output
                response_schema=response_model.model_json_schema(),
            )
            
            # Generate response
            response = await self.generate(request)
            
            # Parse JSON
            try:
                # Debug: log the raw response
                logging.info(f"Raw LLM response for JSON parsing: {response.text[:200]}...")
                
                # Try to extract JSON from response (some models wrap it in text)
                response_text = response.text.strip()
                
                # Look for JSON in the response
                if response_text.startswith('```json'):
                    # Extract JSON from code block
                    start = response_text.find('{')
                    end = response_text.rfind('}') + 1
                    if start != -1 and end > start:
                        response_text = response_text[start:end]
                elif response_text.startswith('```'):
                    # Remove code block markers
                    lines = response_text.split('\n')
                    response_text = '\n'.join(lines[1:-1])
                
                json_response = json.loads(response_text)
            except json.JSONDecodeError as e:
                raise CLIException(
                    "Invalid JSON response from LLM",
                    details={"error": str(e), "response": response.text[:500]}
                )
            
            # Validate against model
            try:
                return response_model.model_validate(json_response)
            except ValidationError as e:
                raise CLIException(
                    "Response validation failed",
                    details={"error": str(e), "response": json_response}
                )
                
        except Exception as e:
            logging.error(f"Structured output generation failed: {e}", exc_info=True)
            raise
    
    def get_available_models(self) -> List[str]:
        """Get list of available models."""
        self._ensure_client()
        return self.forge_client.list_available_models()
    
    def get_recommended_model(self, use_case: str = "general") -> str:
        """Get recommended model for a use case."""
        self._ensure_client()
        return self.forge_client.get_recommended_model(use_case)
    
    def set_default_model(self, model: str):
        """Set the default model for this service instance."""
        if model not in self.get_available_models():
            logging.warning(f"Model {model} not in known model list")
        self.default_model = model
        logging.info(f"Default model set to: {model}")


# Global service instance
_forge_llm_service: Optional[ForgeLLMService] = None


def get_forge_llm_service(default_model: str = "OpenAI/gpt-4.1-nano") -> ForgeLLMService:
    """
    Get the global Forge LLM service instance.
    
    Args:
        default_model: Default model to use
        
    Returns:
        ForgeLLMService instance
    """
    global _forge_llm_service
    
    if _forge_llm_service is None:
        _forge_llm_service = ForgeLLMService(default_model=default_model)
    
    return _forge_llm_service


# Initialize default instance
forge_llm_service = get_forge_llm_service()