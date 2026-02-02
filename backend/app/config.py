# backend/app/config.py
"""
Environment-based configuration management using Pydantic Settings.

This module provides centralized configuration for the API backend,
supporting different environments (development, staging, production).
"""

from functools import lru_cache
from typing import List, Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    
    All settings can be overridden via environment variables or .env file.
    Environment variables take precedence over .env file values.
    """
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )
    
    # ========================
    # Application Settings
    # ========================
    app_name: str = Field(
        default="LLM API Backend",
        description="Application name for logging and metadata"
    )
    app_env: str = Field(
        default="development",
        description="Environment: development, staging, production"
    )
    debug: bool = Field(
        default=False,
        description="Enable debug mode with verbose logging"
    )
    
    # ========================
    # Server Settings
    # ========================
    host: str = Field(
        default="0.0.0.0",
        description="Server host address"
    )
    port: int = Field(
        default=8000,
        description="Server port number"
    )
    workers: int = Field(
        default=1,
        description="Number of worker processes (production)"
    )
    
    # ========================
    # API Security
    # ========================
    api_keys: str = Field(
        default="",
        description="Comma-separated list of valid API keys"
    )
    api_key_header: str = Field(
        default="X-API-Key",
        description="Header name for API key authentication"
    )
    
    # ========================
    # Rate Limiting
    # ========================
    rate_limit_enabled: bool = Field(
        default=True,
        description="Enable rate limiting"
    )
    rate_limit_requests: int = Field(
        default=60,
        description="Maximum requests per minute per API key"
    )
    rate_limit_window_seconds: int = Field(
        default=60,
        description="Rate limit window in seconds"
    )
    
    # ========================
    # CORS Settings
    # ========================
    cors_origins: str = Field(
        default="*",
        description="Comma-separated allowed origins or * for all"
    )
    cors_allow_credentials: bool = Field(
        default=True,
        description="Allow credentials in CORS requests"
    )
    cors_allow_methods: str = Field(
        default="GET,POST,PUT,DELETE,OPTIONS",
        description="Comma-separated allowed HTTP methods"
    )
    cors_allow_headers: str = Field(
        default="*",
        description="Comma-separated allowed headers or * for all"
    )
    
    # ========================
    # Ollama Settings (Primary LLM Provider)
    # ========================
    ollama_base_url: str = Field(
        default="http://localhost:11434",
        description="Ollama API base URL"
    )
    ollama_default_model: str = Field(
        default="llama3.2",
        description="Default Ollama model to use"
    )
    ollama_timeout: int = Field(
        default=120,
        description="Ollama API request timeout in seconds"
    )
    
    # ========================
    # Model Parameters
    # ========================
    default_temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=2.0,
        description="Default temperature for LLM responses"
    )
    default_max_tokens: int = Field(
        default=2048,
        ge=1,
        le=128000,
        description="Default maximum tokens for responses"
    )
    default_top_p: float = Field(
        default=0.9,
        ge=0.0,
        le=1.0,
        description="Default top_p (nucleus sampling) parameter"
    )
    
    # ========================
    # Retry Settings
    # ========================
    retry_max_attempts: int = Field(
        default=3,
        description="Maximum retry attempts for failed requests"
    )
    retry_base_delay: float = Field(
        default=1.0,
        description="Base delay in seconds for exponential backoff"
    )
    retry_max_delay: float = Field(
        default=30.0,
        description="Maximum delay in seconds between retries"
    )
    
    # ========================
    # Logging Settings
    # ========================
    log_level: str = Field(
        default="INFO",
        description="Logging level: DEBUG, INFO, WARNING, ERROR, CRITICAL"
    )
    log_format: str = Field(
        default="json",
        description="Log format: json or console"
    )
    log_requests: bool = Field(
        default=True,
        description="Enable request/response logging"
    )
    
    # ========================
    # Computed Properties
    # ========================
    @property
    def api_keys_list(self) -> List[str]:
        """Parse comma-separated API keys into a list."""
        if not self.api_keys:
            return []
        return [key.strip() for key in self.api_keys.split(",") if key.strip()]
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Parse comma-separated CORS origins into a list."""
        if self.cors_origins == "*":
            return ["*"]
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]
    
    @property
    def cors_methods_list(self) -> List[str]:
        """Parse comma-separated CORS methods into a list."""
        return [method.strip() for method in self.cors_allow_methods.split(",") if method.strip()]
    
    @property
    def cors_headers_list(self) -> List[str]:
        """Parse comma-separated CORS headers into a list."""
        if self.cors_allow_headers == "*":
            return ["*"]
        return [header.strip() for header in self.cors_allow_headers.split(",") if header.strip()]
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.app_env.lower() == "production"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.app_env.lower() == "development"
    
    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate and normalize log level."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        normalized = v.upper()
        if normalized not in valid_levels:
            raise ValueError(f"Invalid log level: {v}. Must be one of {valid_levels}")
        return normalized


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    
    Uses lru_cache to ensure settings are only loaded once,
    improving performance and ensuring consistency.
    
    Returns:
        Settings: The application settings instance
    """
    return Settings()


# Export settings instance for convenience
settings = get_settings()
