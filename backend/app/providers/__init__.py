# backend/app/providers/__init__.py
"""
LLM Provider abstraction layer.

This package provides a pluggable interface for different LLM providers,
with Ollama as the primary implementation for local model hosting.
"""

from .base import LLMProvider, ModelInfo, GenerationConfig, ChatMessage
from .ollama import OllamaProvider
from .registry import ProviderRegistry, get_provider, get_registry

__all__ = [
    "LLMProvider",
    "ModelInfo",
    "GenerationConfig",
    "ChatMessage",
    "OllamaProvider",
    "ProviderRegistry",
    "get_provider",
    "get_registry",
]
