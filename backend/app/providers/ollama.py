# backend/app/providers/ollama.py
"""
Ollama LLM provider implementation.

This module implements the LLM provider interface for Ollama,
enabling local model hosting and inference.

Ollama API Reference: https://github.com/ollama/ollama/blob/main/docs/api.md
"""

import time
from typing import Any, AsyncIterator, Dict, List, Optional

import httpx

from app.config import settings
from app.core.exceptions import ModelNotFoundError, ProviderError
from app.core.logging import get_logger

from .base import (
    ChatMessage,
    GenerationConfig,
    GenerationResult,
    HealthStatus,
    LLMProvider,
    ModelInfo,
    ProviderStatus,
)

logger = get_logger(__name__)


class OllamaProvider(LLMProvider):
    """
    Ollama LLM provider for local model hosting.
    
    Ollama allows running large language models locally. This provider
    connects to a running Ollama instance (default: http://localhost:11434)
    and provides access to all installed models.
    
    Prerequisites:
        - Ollama must be installed: https://ollama.ai
        - Ollama server running: `ollama serve`
        - At least one model pulled: `ollama pull llama3.2`
    
    Attributes:
        base_url: Ollama API base URL
        timeout: Request timeout in seconds
        _default_model: Default model to use
    
    Example:
        >>> provider = OllamaProvider()
        >>> result = await provider.chat([
        ...     ChatMessage(role="user", content="Hello!")
        ... ])
        >>> print(result.content)
    """
    
    def __init__(
        self,
        base_url: Optional[str] = None,
        default_model: Optional[str] = None,
        timeout: Optional[int] = None,
    ) -> None:
        """
        Initialize the Ollama provider.
        
        Args:
            base_url: Ollama API URL (defaults to settings)
            default_model: Default model to use (defaults to settings)
            timeout: Request timeout in seconds (defaults to settings)
        """
        self.base_url = (base_url or settings.ollama_base_url).rstrip("/")
        self._default_model = default_model or settings.ollama_default_model
        self.timeout = timeout or settings.ollama_timeout
        
        logger.info(
            "Ollama provider initialized",
            base_url=self.base_url,
            default_model=self._default_model,
            timeout=self.timeout,
        )
    
    @property
    def name(self) -> str:
        """Get the provider name."""
        return "ollama"
    
    @property
    def default_model(self) -> str:
        """Get the default model."""
        return self._default_model
    
    def _get_client(self) -> httpx.AsyncClient:
        """Create an async HTTP client with configured timeout."""
        return httpx.AsyncClient(
            base_url=self.base_url,
            timeout=httpx.Timeout(self.timeout),
        )
    
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        json_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Make an HTTP request to Ollama API.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            json_data: Request body as dictionary
        
        Returns:
            Response data as dictionary
        
        Raises:
            ProviderError: If the request fails
        """
        async with self._get_client() as client:
            try:
                response = await client.request(
                    method=method,
                    url=endpoint,
                    json=json_data,
                )
                
                if response.status_code >= 400:
                    error_text = response.text
                    logger.error(
                        "Ollama API error",
                        status_code=response.status_code,
                        error=error_text,
                    )
                    raise ProviderError(
                        message=f"Ollama API error: {error_text}",
                        provider=self.name,
                        details={"status_code": response.status_code},
                    )
                
                return response.json()
                
            except httpx.ConnectError as e:
                logger.error(
                    "Failed to connect to Ollama",
                    base_url=self.base_url,
                    error=str(e),
                )
                raise ProviderError(
                    message="Failed to connect to Ollama. Is it running?",
                    provider=self.name,
                    is_unavailable=True,
                    details={"url": self.base_url},
                )
            except httpx.TimeoutException as e:
                logger.error(
                    "Ollama request timed out",
                    timeout=self.timeout,
                    error=str(e),
                )
                raise ProviderError(
                    message=f"Ollama request timed out after {self.timeout}s",
                    provider=self.name,
                    details={"timeout_seconds": self.timeout},
                )
    
    async def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        config: Optional[GenerationConfig] = None,
    ) -> GenerationResult:
        """
        Generate text from a prompt using Ollama.
        
        Uses the /api/generate endpoint for completion-style generation.
        
        Args:
            prompt: The input prompt
            model: Model to use (defaults to provider default)
            config: Generation configuration
        
        Returns:
            GenerationResult with the generated text
        """
        model = model or self._default_model
        config = config or self.get_default_config()
        
        logger.debug(
            "Generating text",
            model=model,
            prompt_length=len(prompt),
            temperature=config.temperature,
        )
        
        start_time = time.time()
        
        # Build request payload
        payload: Dict[str, Any] = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": config.temperature,
                "num_predict": config.max_tokens,
                "top_p": config.top_p,
            },
        }
        
        if config.top_k is not None:
            payload["options"]["top_k"] = config.top_k
        
        if config.stop_sequences:
            payload["options"]["stop"] = config.stop_sequences
        
        if config.seed is not None:
            payload["options"]["seed"] = config.seed
        
        try:
            response = await self._make_request("POST", "/api/generate", payload)
        except ProviderError as e:
            if "not found" in str(e).lower():
                raise ModelNotFoundError(model=model, provider=self.name)
            raise
        
        elapsed_ms = (time.time() - start_time) * 1000
        
        # Parse response
        content = response.get("response", "")
        
        usage = {
            "prompt_tokens": response.get("prompt_eval_count", 0),
            "completion_tokens": response.get("eval_count", 0),
            "total_tokens": (
                response.get("prompt_eval_count", 0) + 
                response.get("eval_count", 0)
            ),
        }
        
        logger.info(
            "Text generated",
            model=model,
            tokens=usage["total_tokens"],
            latency_ms=round(elapsed_ms, 2),
        )
        
        return GenerationResult(
            content=content,
            model=model,
            finish_reason="stop" if response.get("done") else "length",
            usage=usage,
            metadata={
                "latency_ms": round(elapsed_ms, 2),
                "provider": self.name,
            },
        )
    
    async def chat(
        self,
        messages: List[ChatMessage],
        model: Optional[str] = None,
        config: Optional[GenerationConfig] = None,
    ) -> GenerationResult:
        """
        Generate a chat completion using Ollama.
        
        Uses the /api/chat endpoint for conversational generation.
        
        Args:
            messages: List of chat messages
            model: Model to use
            config: Generation configuration
        
        Returns:
            GenerationResult with the assistant's response
        """
        model = model or self._default_model
        config = config or self.get_default_config()
        
        logger.debug(
            "Chat completion",
            model=model,
            message_count=len(messages),
        )
        
        start_time = time.time()
        
        # Convert messages to Ollama format
        ollama_messages = [msg.to_dict() for msg in messages]
        
        # Build request payload
        payload: Dict[str, Any] = {
            "model": model,
            "messages": ollama_messages,
            "stream": False,
            "options": {
                "temperature": config.temperature,
                "num_predict": config.max_tokens,
                "top_p": config.top_p,
            },
        }
        
        if config.top_k is not None:
            payload["options"]["top_k"] = config.top_k
        
        if config.stop_sequences:
            payload["options"]["stop"] = config.stop_sequences
        
        if config.seed is not None:
            payload["options"]["seed"] = config.seed
        
        try:
            response = await self._make_request("POST", "/api/chat", payload)
        except ProviderError as e:
            if "not found" in str(e).lower():
                raise ModelNotFoundError(model=model, provider=self.name)
            raise
        
        elapsed_ms = (time.time() - start_time) * 1000
        
        # Parse response
        message = response.get("message", {})
        content = message.get("content", "")
        
        usage = {
            "prompt_tokens": response.get("prompt_eval_count", 0),
            "completion_tokens": response.get("eval_count", 0),
            "total_tokens": (
                response.get("prompt_eval_count", 0) + 
                response.get("eval_count", 0)
            ),
        }
        
        logger.info(
            "Chat completed",
            model=model,
            tokens=usage["total_tokens"],
            latency_ms=round(elapsed_ms, 2),
        )
        
        return GenerationResult(
            content=content,
            model=model,
            finish_reason="stop" if response.get("done") else "length",
            usage=usage,
            metadata={
                "latency_ms": round(elapsed_ms, 2),
                "provider": self.name,
            },
        )
    
    async def chat_stream(
        self,
        messages: List[ChatMessage],
        model: Optional[str] = None,
        config: Optional[GenerationConfig] = None,
    ) -> AsyncIterator[str]:
        """
        Stream a chat completion from Ollama.
        
        Yields chunks of the response as they are generated.
        
        Args:
            messages: List of chat messages
            model: Model to use
            config: Generation configuration
        
        Yields:
            Text chunks as they are generated
        """
        model = model or self._default_model
        config = config or self.get_default_config()
        
        logger.debug(
            "Streaming chat",
            model=model,
            message_count=len(messages),
        )
        
        ollama_messages = [msg.to_dict() for msg in messages]
        
        payload: Dict[str, Any] = {
            "model": model,
            "messages": ollama_messages,
            "stream": True,
            "options": {
                "temperature": config.temperature,
                "num_predict": config.max_tokens,
                "top_p": config.top_p,
            },
        }
        
        async with self._get_client() as client:
            try:
                async with client.stream(
                    "POST",
                    "/api/chat",
                    json=payload,
                ) as response:
                    if response.status_code >= 400:
                        error_text = await response.aread()
                        raise ProviderError(
                            message=f"Ollama streaming error: {error_text}",
                            provider=self.name,
                        )
                    
                    async for line in response.aiter_lines():
                        if line:
                            import json
                            try:
                                data = json.loads(line)
                                message = data.get("message", {})
                                content = message.get("content", "")
                                if content:
                                    yield content
                                if data.get("done"):
                                    break
                            except json.JSONDecodeError:
                                continue
                                
            except httpx.ConnectError:
                raise ProviderError(
                    message="Failed to connect to Ollama for streaming",
                    provider=self.name,
                    is_unavailable=True,
                )
    
    async def list_models(self) -> List[ModelInfo]:
        """
        List all available models in Ollama.
        
        Uses the /api/tags endpoint to get installed models.
        
        Returns:
            List of ModelInfo for each installed model
        """
        logger.debug("Listing Ollama models")
        
        try:
            response = await self._make_request("GET", "/api/tags", None)
        except ProviderError:
            logger.warning("Failed to list models, returning empty list")
            return []
        
        models = []
        for model_data in response.get("models", []):
            model_info = ModelInfo(
                name=model_data.get("name", "unknown"),
                provider=self.name,
                size=model_data.get("size"),
                modified_at=model_data.get("modified_at"),
                capabilities=["chat", "generate"],
                parameters={
                    "family": model_data.get("details", {}).get("family"),
                    "parameter_size": model_data.get("details", {}).get("parameter_size"),
                    "quantization": model_data.get("details", {}).get("quantization_level"),
                },
            )
            models.append(model_info)
        
        logger.info("Models listed", count=len(models))
        return models
    
    async def health_check(self) -> HealthStatus:
        """
        Check Ollama health status.
        
        Verifies connectivity and counts available models.
        
        Returns:
            HealthStatus indicating Ollama's current state
        """
        start_time = time.time()
        
        try:
            models = await self.list_models()
            latency_ms = (time.time() - start_time) * 1000
            
            if not models:
                return HealthStatus(
                    status=ProviderStatus.DEGRADED,
                    latency_ms=latency_ms,
                    available_models=0,
                    message="Ollama is running but no models are installed",
                    details={"suggestion": "Run 'ollama pull llama3.2' to install a model"},
                )
            
            return HealthStatus(
                status=ProviderStatus.HEALTHY,
                latency_ms=round(latency_ms, 2),
                available_models=len(models),
                message="Ollama is healthy",
                details={"models": [m.name for m in models[:5]]},  # First 5 models
            )
            
        except ProviderError as e:
            latency_ms = (time.time() - start_time) * 1000
            return HealthStatus(
                status=ProviderStatus.UNAVAILABLE,
                latency_ms=round(latency_ms, 2),
                available_models=0,
                message=str(e),
                details={"base_url": self.base_url},
            )
    
    async def pull_model(self, model: str) -> bool:
        """
        Pull/download a model from Ollama registry.
        
        This is a convenience method for downloading new models.
        Note: This can take a long time for large models.
        
        Args:
            model: Model name to pull (e.g., "llama3.2")
        
        Returns:
            True if successful
        
        Raises:
            ProviderError: If pull fails
        """
        logger.info("Pulling model", model=model)
        
        async with self._get_client() as client:
            try:
                # Ollama pull endpoint streams progress
                async with client.stream(
                    "POST",
                    "/api/pull",
                    json={"name": model},
                ) as response:
                    if response.status_code >= 400:
                        raise ProviderError(
                            message=f"Failed to pull model: {model}",
                            provider=self.name,
                        )
                    
                    # Consume the stream to complete the pull
                    async for _ in response.aiter_bytes():
                        pass
                    
                logger.info("Model pulled successfully", model=model)
                return True
                
            except httpx.ConnectError:
                raise ProviderError(
                    message="Failed to connect to Ollama",
                    provider=self.name,
                    is_unavailable=True,
                )
