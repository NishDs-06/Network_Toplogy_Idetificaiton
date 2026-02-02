# backend/app/providers/registry.py
"""
Provider registry for managing LLM providers.

This module provides a factory pattern for creating and managing
LLM provider instances, enabling runtime switching between providers.
"""

from functools import lru_cache
from typing import Dict, List, Optional, Type

from app.config import settings
from app.core.exceptions import ProviderError
from app.core.logging import get_logger

from .base import LLMProvider, ModelInfo
from .ollama import OllamaProvider

logger = get_logger(__name__)


# Registry of available provider classes
_PROVIDER_REGISTRY: Dict[str, Type[LLMProvider]] = {
    "ollama": OllamaProvider,
}


class ProviderRegistry:
    """
    Registry for managing LLM provider instances.
    
    This class provides:
    - Provider instance caching (singleton per provider)
    - Runtime provider switching
    - Default provider management
    - Model availability checking across providers
    
    The registry follows a singleton pattern where each provider
    type has only one instance, enabling efficient resource usage.
    
    Example:
        >>> registry = ProviderRegistry()
        >>> provider = registry.get_provider("ollama")
        >>> result = await provider.chat([...])
    """
    
    def __init__(self) -> None:
        """Initialize the provider registry."""
        self._instances: Dict[str, LLMProvider] = {}
        self._default_provider: str = "ollama"
        self._default_model: Optional[str] = None
        
        logger.info(
            "Provider registry initialized",
            available_providers=list(_PROVIDER_REGISTRY.keys()),
            default_provider=self._default_provider,
        )
    
    @property
    def available_providers(self) -> List[str]:
        """Get list of available provider names."""
        return list(_PROVIDER_REGISTRY.keys())
    
    @property
    def default_provider_name(self) -> str:
        """Get the current default provider name."""
        return self._default_provider
    
    @property
    def default_model_name(self) -> Optional[str]:
        """Get the current default model name."""
        return self._default_model
    
    def get_provider(self, name: Optional[str] = None) -> LLMProvider:
        """
        Get a provider instance by name.
        
        Provider instances are cached and reused. If no name is provided,
        returns the default provider.
        
        Args:
            name: Provider name (e.g., "ollama"). Defaults to default provider.
        
        Returns:
            The LLM provider instance
        
        Raises:
            ProviderError: If the provider is not registered
        """
        provider_name = name or self._default_provider
        
        # Return cached instance if available
        if provider_name in self._instances:
            return self._instances[provider_name]
        
        # Check if provider is registered
        if provider_name not in _PROVIDER_REGISTRY:
            raise ProviderError(
                message=f"Unknown provider: {provider_name}",
                provider=provider_name,
                details={"available_providers": self.available_providers},
            )
        
        # Create and cache new instance
        provider_class = _PROVIDER_REGISTRY[provider_name]
        instance = provider_class()
        self._instances[provider_name] = instance
        
        logger.info(
            "Provider instance created",
            provider=provider_name,
            default_model=instance.default_model,
        )
        
        return instance
    
    def get_default_provider(self) -> LLMProvider:
        """
        Get the default provider instance.
        
        Returns:
            The default LLM provider instance
        """
        return self.get_provider(self._default_provider)
    
    def set_default_provider(self, name: str, model: Optional[str] = None) -> None:
        """
        Set the default provider and optionally the default model.
        
        Args:
            name: Provider name to set as default
            model: Optional model name to set as default
        
        Raises:
            ProviderError: If the provider is not registered
        """
        if name not in _PROVIDER_REGISTRY:
            raise ProviderError(
                message=f"Cannot set default: unknown provider '{name}'",
                provider=name,
                details={"available_providers": self.available_providers},
            )
        
        old_provider = self._default_provider
        self._default_provider = name
        self._default_model = model
        
        logger.info(
            "Default provider changed",
            old_provider=old_provider,
            new_provider=name,
            model=model,
        )
    
    def register_provider(self, name: str, provider_class: Type[LLMProvider]) -> None:
        """
        Register a new provider class.
        
        This allows adding custom providers at runtime.
        
        Args:
            name: Unique identifier for the provider
            provider_class: Provider class that implements LLMProvider
        
        Raises:
            ValueError: If the provider class is invalid
        """
        if not issubclass(provider_class, LLMProvider):
            raise ValueError(
                f"Provider class must inherit from LLMProvider: {provider_class}"
            )
        
        _PROVIDER_REGISTRY[name] = provider_class
        
        logger.info("Provider registered", provider=name)
    
    def unregister_provider(self, name: str) -> None:
        """
        Unregister a provider.
        
        Args:
            name: Provider name to unregister
        """
        if name in _PROVIDER_REGISTRY:
            del _PROVIDER_REGISTRY[name]
        
        if name in self._instances:
            del self._instances[name]
        
        if self._default_provider == name:
            # Fall back to first available provider
            if _PROVIDER_REGISTRY:
                self._default_provider = next(iter(_PROVIDER_REGISTRY))
            else:
                self._default_provider = ""
        
        logger.info("Provider unregistered", provider=name)
    
    async def list_all_models(self) -> Dict[str, List[ModelInfo]]:
        """
        List models from all providers.
        
        Returns:
            Dictionary mapping provider names to their available models
        """
        all_models: Dict[str, List[ModelInfo]] = {}
        
        for provider_name in self.available_providers:
            try:
                provider = self.get_provider(provider_name)
                models = await provider.list_models()
                all_models[provider_name] = models
            except Exception as e:
                logger.warning(
                    "Failed to list models from provider",
                    provider=provider_name,
                    error=str(e),
                )
                all_models[provider_name] = []
        
        return all_models
    
    async def get_health_status(self) -> Dict[str, dict]:
        """
        Get health status of all providers.
        
        Returns:
            Dictionary mapping provider names to their health status
        """
        health_status: Dict[str, dict] = {}
        
        for provider_name in self.available_providers:
            try:
                provider = self.get_provider(provider_name)
                status = await provider.health_check()
                health_status[provider_name] = status.to_dict()
            except Exception as e:
                health_status[provider_name] = {
                    "status": "error",
                    "message": str(e),
                }
        
        return health_status
    
    def clear_cache(self) -> None:
        """Clear all cached provider instances."""
        self._instances.clear()
        logger.info("Provider cache cleared")


# Global registry instance
_registry: Optional[ProviderRegistry] = None


def get_registry() -> ProviderRegistry:
    """
    Get the global provider registry instance.
    
    Uses lazy initialization to create the registry on first access.
    
    Returns:
        The global ProviderRegistry instance
    """
    global _registry
    if _registry is None:
        _registry = ProviderRegistry()
    return _registry


def get_provider(name: Optional[str] = None) -> LLMProvider:
    """
    Convenience function to get a provider from the global registry.
    
    Args:
        name: Provider name (defaults to default provider)
    
    Returns:
        The requested LLM provider instance
    """
    return get_registry().get_provider(name)
