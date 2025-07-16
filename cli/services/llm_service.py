"""
CLI-adapted LLM Service - Removes web dependencies from app.services.llm_service
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from pydantic import BaseModel
import os
import logging
import openai
from dotenv import load_dotenv
from app.services.circuit_breaker import CircuitBreaker
import json
from pydantic import ValidationError

load_dotenv()

# Circuit Breaker config for LLM providers
LLM_CIRCUIT_BREAKER_FAILURE_THRESHOLD: int = int(
    os.getenv("LLM_CIRCUIT_BREAKER_FAILURE_THRESHOLD", 5)
)
LLM_CIRCUIT_BREAKER_RECOVERY_TIMEOUT: int = int(
    os.getenv("LLM_CIRCUIT_BREAKER_RECOVERY_TIMEOUT", 300)
)
LLM_CIRCUIT_BREAKER_DISABLE: bool = (
    os.getenv("LLM_CIRCUIT_BREAKER_DISABLE", "false").lower() == "true"
)


class CLIException(Exception):
    """CLI-specific exception to replace HTTPException"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.details = details or {}
        super().__init__(message)


class LLMRequest(BaseModel):
    """Standardized input model for LLM requests."""
    
    system_prompt: Optional[str] = None
    user_prompt: str
    parameters: Optional[Dict[str, Any]] = None
    response_schema: Optional[Dict[str, Any]] = None

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


class BaseLLMProvider(ABC):
    """Abstract base class for all LLM provider adapters."""
    
    name: str
    priority: int

    @abstractmethod
    async def generate(self, request: LLMRequest) -> LLMResponse:
        """Generate a response from the LLM provider."""
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """Check if the provider is healthy/available."""
        pass


class OpenAIProvider(BaseLLMProvider):
    """Adapter for the OpenAI LLM provider."""
    
    name = "openai"
    priority = 1

    def __init__(self) -> None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            logging.error("OPENAI_API_KEY is not set in the environment.")
            raise ValueError("OPENAI_API_KEY is required.")
        self.client = openai.OpenAI(api_key=api_key)
        self.model = "gpt-4.1-nano"

    async def generate(self, request: LLMRequest) -> LLMResponse:
        """Generate text using OpenAI API, supporting structured output via response_format."""
        try:
            import asyncio

            kwargs = request.parameters.copy() if request.parameters else {}

            if request.response_schema:
                kwargs["response_format"] = {"type": "json_object"}

            messages = []
            if request.system_prompt:
                messages.append({"role": "system", "content": request.system_prompt})

            user_content = request.user_prompt
            if request.response_schema and "json" not in user_content.lower():
                user_content += "\n\nRespond in JSON format."
            messages.append({"role": "user", "content": user_content})

            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    **kwargs,
                ),
            )
            text = response.choices[0].message.content if response.choices else ""
            usage = dict(response.usage) if hasattr(response, "usage") else None
            return LLMResponse(
                text=text, model=self.model, provider=self.name, usage=usage
            )
        except Exception as e:
            import traceback
            traceback.print_exc()
            logging.error(f"OpenAIProvider error: {e}", exc_info=True)
            raise

    async def health_check(self) -> bool:
        """Check if OpenAI API is available by making a lightweight call."""
        try:
            import asyncio
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.client.chat.completions.create(
                    model=self.model, messages=[{"role": "user", "content": "ping"}]
                ),
            )
            return True
        except Exception as e:
            logging.warning(f"OpenAIProvider health check failed: {e}", exc_info=True)
            return False


class LLMClient:
    """Orchestrates LLM provider selection, failover, and exposes a unified API."""

    def __init__(self, providers: Optional[List[BaseLLMProvider]] = None) -> None:
        self.providers: List[BaseLLMProvider] = providers or []
        self.providers.sort(key=lambda p: p.priority)
        logging.info(
            f"LLMClient initialized with providers: {[p.name for p in self.providers]}"
        )
        # CircuitBreaker per provider
        self.circuit_breakers: Dict[str, CircuitBreaker] = {
            p.name: CircuitBreaker(
                provider_name=p.name,
                failure_threshold=LLM_CIRCUIT_BREAKER_FAILURE_THRESHOLD,
                recovery_timeout=LLM_CIRCUIT_BREAKER_RECOVERY_TIMEOUT,
                disable=LLM_CIRCUIT_BREAKER_DISABLE,
            )
            for p in self.providers
        }

    def register_provider(self, provider: BaseLLMProvider) -> None:
        """Register a new LLM provider and sort by priority."""
        self.providers.append(provider)
        self.providers.sort(key=lambda p: p.priority)
        self.circuit_breakers[provider.name] = CircuitBreaker(
            provider_name=provider.name,
            failure_threshold=LLM_CIRCUIT_BREAKER_FAILURE_THRESHOLD,
            recovery_timeout=LLM_CIRCUIT_BREAKER_RECOVERY_TIMEOUT,
            disable=LLM_CIRCUIT_BREAKER_DISABLE,
        )

    async def generate_structured_output(
        self,
        prompt: str,
        response_model: type[BaseModel],
        system_prompt: Optional[str] = None,
    ) -> BaseModel:
        """Generate structured output using the LLM and validate against a Pydantic model."""
        try:
            # Create a request with JSON output format
            request = LLMRequest(
                user_prompt=prompt,
                system_prompt=system_prompt,
                parameters={"temperature": 0.1},
                response_schema=response_model.model_json_schema(),
            )

            # Generate response
            response = await self.generate(request)

            # Parse and validate response
            try:
                json_response = json.loads(response.text)
            except json.JSONDecodeError as e:
                raise CLIException(
                    "Invalid JSON response from LLM",
                    details={"error": str(e)}
                )

            # Validate against the model
            try:
                return response_model.model_validate(json_response)
            except ValidationError as e:
                raise CLIException(
                    "Response validation failed",
                    details={"error": str(e)}
                )
        except Exception as e:
            logging.error(f"LLMService error: {e}", exc_info=True)
            raise

    async def generate(self, request: LLMRequest) -> LLMResponse:
        """Try providers in order of priority, with failover on error and circuit breaker logic."""
        for provider in self.providers:
            cb = self.circuit_breakers[provider.name]
            if not await cb.can_execute():
                print(f"Circuit breaker OPEN for provider: {provider.name}, skipping.")
                continue
            try:
                model_name = getattr(provider, "model", None)
                if model_name:
                    print(f"Using LLM Model: {provider.name} (model: {model_name})")
                else:
                    print(f"Using LLM Model: {provider.name}")
                response = await provider.generate(request)
                await cb.record_success()
                return response
            except Exception as e:
                print("=== LLM CLIENT ERROR ===")
                print(e)
                import traceback
                traceback.print_exc()
                logging.error(f"LLMService error: {e}", exc_info=True)
                await cb.record_failure()
                # Continue to next provider
        print("All providers failed or are unavailable.")
        raise RuntimeError("All LLM providers failed or are unavailable.")