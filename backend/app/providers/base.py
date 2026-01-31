# backend/app/providers/base.py
"""
Abstract base class for LLM providers.

This module defines the interface that all LLM providers must implement,
ensuring consistent behavior regardless of the underlying model/service.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, AsyncIterator, Dict, List, Optional


class ProviderStatus(str, Enum):
    """Status of an LLM provider."""
    
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNAVAILABLE = "unavailable"
    UNKNOWN = "unknown"


@dataclass
class ModelInfo:
    """
    Information about an available model.
    
    Attributes:
        name: Model identifier (e.g., "llama3.2", "mistral")
        provider: Provider name (e.g., "ollama", "openai")
        size: Model size in bytes (if known)
        modified_at: Last modification timestamp
        capabilities: List of model capabilities
        parameters: Model-specific parameters
    """
    
    name: str
    provider: str
    size: Optional[int] = None
    modified_at: Optional[str] = None
    capabilities: List[str] = field(default_factory=lambda: ["chat", "generate"])
    parameters: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "name": self.name,
            "provider": self.provider,
            "size": self.size,
            "modified_at": self.modified_at,
            "capabilities": self.capabilities,
            "parameters": self.parameters,
        }


@dataclass
class ChatMessage:
    """
    A single message in a chat conversation.
    
    Attributes:
        role: Message role (system, user, assistant)
        content: Message content text
        name: Optional name for the message author
        metadata: Optional additional metadata
    """
    
    role: str  # "system", "user", "assistant"
    content: str
    name: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API requests."""
        result = {"role": self.role, "content": self.content}
        if self.name:
            result["name"] = self.name
        return result


@dataclass
class GenerationConfig:
    """
    Configuration for text generation.
    
    This dataclass encapsulates all parameters that control
    how the LLM generates responses.
    
    Attributes:
        temperature: Controls randomness (0.0 = deterministic, 2.0 = very random)
        max_tokens: Maximum number of tokens to generate
        top_p: Nucleus sampling parameter
        top_k: Top-k sampling parameter
        stop_sequences: Sequences that stop generation
        presence_penalty: Penalty for new topics
        frequency_penalty: Penalty for repeated tokens
        seed: Random seed for reproducibility
    """
    
    temperature: float = 0.7
    max_tokens: int = 2048
    top_p: float = 0.9
    top_k: Optional[int] = None
    stop_sequences: List[str] = field(default_factory=list)
    presence_penalty: float = 0.0
    frequency_penalty: float = 0.0
    seed: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API requests."""
        result = {
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "top_p": self.top_p,
        }
        if self.top_k is not None:
            result["top_k"] = self.top_k
        if self.stop_sequences:
            result["stop"] = self.stop_sequences
        if self.presence_penalty != 0.0:
            result["presence_penalty"] = self.presence_penalty
        if self.frequency_penalty != 0.0:
            result["frequency_penalty"] = self.frequency_penalty
        if self.seed is not None:
            result["seed"] = self.seed
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GenerationConfig":
        """Create config from dictionary."""
        return cls(
            temperature=data.get("temperature", 0.7),
            max_tokens=data.get("max_tokens", 2048),
            top_p=data.get("top_p", 0.9),
            top_k=data.get("top_k"),
            stop_sequences=data.get("stop", []),
            presence_penalty=data.get("presence_penalty", 0.0),
            frequency_penalty=data.get("frequency_penalty", 0.0),
            seed=data.get("seed"),
        )


@dataclass
class GenerationResult:
    """
    Result of a text generation request.
    
    Attributes:
        content: Generated text content
        model: Model that generated the response
        finish_reason: Why generation stopped
        usage: Token usage statistics
        metadata: Additional metadata
    """
    
    content: str
    model: str
    finish_reason: str = "stop"
    usage: Dict[str, int] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "content": self.content,
            "model": self.model,
            "finish_reason": self.finish_reason,
            "usage": self.usage,
            "metadata": self.metadata,
        }


@dataclass
class HealthStatus:
    """
    Health status of a provider.
    
    Attributes:
        status: Overall status
        latency_ms: Response latency in milliseconds
        available_models: Number of available models
        message: Status message
        details: Additional details
    """
    
    status: ProviderStatus
    latency_ms: Optional[float] = None
    available_models: int = 0
    message: str = ""
    details: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "status": self.status.value,
            "latency_ms": self.latency_ms,
            "available_models": self.available_models,
            "message": self.message,
            "details": self.details,
        }


class LLMProvider(ABC):
    """
    Abstract base class for LLM providers.
    
    All LLM providers (Ollama, OpenAI, Anthropic, etc.) must implement
    this interface to ensure consistent behavior across the application.
    
    Subclasses should:
    1. Implement all abstract methods
    2. Handle provider-specific errors gracefully
    3. Map provider responses to the standard result types
    4. Implement proper async patterns for I/O operations
    
    Example:
        >>> class MyProvider(LLMProvider):
        ...     async def generate(self, prompt, model, config):
        ...         # Implementation here
        ...         pass
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """
        Get the provider name.
        
        Returns:
            Unique identifier for this provider (e.g., "ollama", "openai")
        """
        pass
    
    @property
    @abstractmethod
    def default_model(self) -> str:
        """
        Get the default model for this provider.
        
        Returns:
            The default model identifier to use when not specified
        """
        pass
    
    @abstractmethod
    async def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        config: Optional[GenerationConfig] = None,
    ) -> GenerationResult:
        """
        Generate text from a prompt.
        
        This is the core generation method for simple prompt-to-completion
        use cases like summarization, extraction, etc.
        
        Args:
            prompt: The input prompt text
            model: Model to use (defaults to provider's default)
            config: Generation configuration
        
        Returns:
            GenerationResult containing the generated text
        
        Raises:
            ProviderError: If the provider encounters an error
            ModelNotFoundError: If the specified model is not available
        """
        pass
    
    @abstractmethod
    async def chat(
        self,
        messages: List[ChatMessage],
        model: Optional[str] = None,
        config: Optional[GenerationConfig] = None,
    ) -> GenerationResult:
        """
        Generate a chat completion.
        
        This method handles multi-turn conversations with system prompts,
        user messages, and assistant responses.
        
        Args:
            messages: List of chat messages (conversation history)
            model: Model to use (defaults to provider's default)
            config: Generation configuration
        
        Returns:
            GenerationResult containing the assistant's response
        
        Raises:
            ProviderError: If the provider encounters an error
            ModelNotFoundError: If the specified model is not available
        """
        pass
    
    @abstractmethod
    async def chat_stream(
        self,
        messages: List[ChatMessage],
        model: Optional[str] = None,
        config: Optional[GenerationConfig] = None,
    ) -> AsyncIterator[str]:
        """
        Stream a chat completion.
        
        Similar to chat() but yields chunks of the response as they
        are generated, enabling real-time streaming to clients.
        
        Args:
            messages: List of chat messages (conversation history)
            model: Model to use (defaults to provider's default)
            config: Generation configuration
        
        Yields:
            Chunks of generated text as they become available
        
        Raises:
            ProviderError: If the provider encounters an error
        """
        pass
    
    @abstractmethod
    async def list_models(self) -> List[ModelInfo]:
        """
        List all available models.
        
        Returns:
            List of ModelInfo objects for each available model
        
        Raises:
            ProviderError: If the provider encounters an error
        """
        pass
    
    @abstractmethod
    async def health_check(self) -> HealthStatus:
        """
        Check the health of this provider.
        
        This method should verify connectivity and basic functionality
        without making expensive API calls.
        
        Returns:
            HealthStatus indicating the provider's current state
        """
        pass
    
    async def supports_model(self, model: str) -> bool:
        """
        Check if a specific model is supported.
        
        Args:
            model: Model identifier to check
        
        Returns:
            True if the model is available, False otherwise
        """
        try:
            models = await self.list_models()
            return any(m.name == model for m in models)
        except Exception:
            return False
    
    def get_default_config(self) -> GenerationConfig:
        """
        Get the default generation configuration.
        
        Subclasses can override this to provide provider-specific defaults.
        
        Returns:
            Default GenerationConfig for this provider
        """
        return GenerationConfig()
