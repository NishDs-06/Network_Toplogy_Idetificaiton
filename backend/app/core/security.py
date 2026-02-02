# backend/app/core/security.py
"""
Security utilities for API authentication and rate limiting.

This module provides:
- API key validation
- In-memory rate limiting with sliding window
- Security-related helper functions
"""

import hashlib
import time
from collections import defaultdict
from dataclasses import dataclass, field
from threading import Lock
from typing import Dict, List, Optional, Tuple

from app.config import settings
from app.core.exceptions import AuthenticationError, RateLimitExceeded
from app.core.logging import get_logger

logger = get_logger(__name__)


def hash_api_key(api_key: str) -> str:
    """
    Create a safe hash of an API key for logging/identification.
    
    We never log full API keys. This creates a short hash that can
    be used to identify which key was used without exposing it.
    
    Args:
        api_key: The full API key
    
    Returns:
        A short hash string (first 8 chars of SHA256)
    """
    return hashlib.sha256(api_key.encode()).hexdigest()[:8]


def validate_api_key(api_key: Optional[str]) -> str:
    """
    Validate an API key against the configured valid keys.
    
    Args:
        api_key: The API key to validate (from request header)
    
    Returns:
        The hashed key ID for logging
    
    Raises:
        AuthenticationError: If the key is missing or invalid
    """
    if not api_key:
        logger.warning("Missing API key in request")
        raise AuthenticationError("Missing API key")
    
    valid_keys = settings.api_keys_list
    
    # If no keys configured, allow all (development mode warning)
    if not valid_keys:
        logger.warning(
            "No API keys configured - authentication disabled",
            security_warning=True,
        )
        return "no-auth"
    
    if api_key not in valid_keys:
        key_hash = hash_api_key(api_key)
        logger.warning(
            "Invalid API key attempted",
            key_hash=key_hash,
        )
        raise AuthenticationError("Invalid API key")
    
    return hash_api_key(api_key)


@dataclass
class RateLimitEntry:
    """
    Represents a rate limit tracking entry for a single API key.
    
    Uses a sliding window approach where we track individual
    request timestamps and remove expired ones.
    """
    
    requests: List[float] = field(default_factory=list)
    lock: Lock = field(default_factory=Lock)
    
    def add_request(self, timestamp: float, window_seconds: int) -> None:
        """Add a request timestamp and clean up expired entries."""
        with self.lock:
            # Remove expired timestamps
            cutoff = timestamp - window_seconds
            self.requests = [ts for ts in self.requests if ts > cutoff]
            # Add new timestamp
            self.requests.append(timestamp)
    
    def get_count(self, window_seconds: int) -> int:
        """Get the number of requests in the current window."""
        cutoff = time.time() - window_seconds
        with self.lock:
            return sum(1 for ts in self.requests if ts > cutoff)
    
    def time_until_reset(self, window_seconds: int) -> int:
        """Calculate seconds until the oldest request expires."""
        if not self.requests:
            return 0
        oldest = min(self.requests)
        reset_time = oldest + window_seconds
        return max(0, int(reset_time - time.time()))


class RateLimiter:
    """
    In-memory rate limiter with sliding window algorithm.
    
    This implementation uses a sliding window approach that provides
    smoother rate limiting compared to fixed windows. Each API key
    has its own counter that tracks requests within the time window.
    
    Note: This is an in-memory implementation. For distributed systems,
    use Redis or a similar distributed cache.
    
    Attributes:
        max_requests: Maximum requests allowed per window
        window_seconds: Time window in seconds
    """
    
    def __init__(
        self,
        max_requests: Optional[int] = None,
        window_seconds: Optional[int] = None,
    ) -> None:
        """
        Initialize the rate limiter.
        
        Args:
            max_requests: Max requests per window (defaults to settings)
            window_seconds: Window size in seconds (defaults to settings)
        """
        self.max_requests = max_requests or settings.rate_limit_requests
        self.window_seconds = window_seconds or settings.rate_limit_window_seconds
        self._entries: Dict[str, RateLimitEntry] = defaultdict(RateLimitEntry)
        self._lock = Lock()
        
        logger.info(
            "Rate limiter initialized",
            max_requests=self.max_requests,
            window_seconds=self.window_seconds,
        )
    
    def check_rate_limit(self, key: str) -> Tuple[bool, int, int]:
        """
        Check if a request is within rate limits.
        
        Args:
            key: Identifier for rate limiting (usually hashed API key)
        
        Returns:
            Tuple of (allowed, remaining, reset_seconds)
        """
        now = time.time()
        
        with self._lock:
            entry = self._entries[key]
        
        # Get current count before adding new request
        current_count = entry.get_count(self.window_seconds)
        
        if current_count >= self.max_requests:
            reset_seconds = entry.time_until_reset(self.window_seconds)
            return False, 0, reset_seconds
        
        # Add the request
        entry.add_request(now, self.window_seconds)
        remaining = self.max_requests - current_count - 1
        
        return True, remaining, self.window_seconds
    
    def enforce_rate_limit(self, key: str) -> Dict[str, int]:
        """
        Enforce rate limit and raise exception if exceeded.
        
        Args:
            key: Identifier for rate limiting
        
        Returns:
            Dictionary with rate limit headers info
        
        Raises:
            RateLimitExceeded: If rate limit is exceeded
        """
        allowed, remaining, reset_seconds = self.check_rate_limit(key)
        
        headers_info = {
            "X-RateLimit-Limit": self.max_requests,
            "X-RateLimit-Remaining": remaining,
            "X-RateLimit-Reset": reset_seconds,
        }
        
        if not allowed:
            logger.warning(
                "Rate limit exceeded",
                key=key,
                reset_seconds=reset_seconds,
            )
            raise RateLimitExceeded(
                retry_after=reset_seconds,
                details={
                    "limit": self.max_requests,
                    "window_seconds": self.window_seconds,
                },
            )
        
        return headers_info
    
    def get_usage(self, key: str) -> Dict[str, int]:
        """
        Get current usage statistics for a key.
        
        Args:
            key: Identifier to check
        
        Returns:
            Dictionary with usage info
        """
        with self._lock:
            entry = self._entries.get(key)
        
        if not entry:
            return {
                "current": 0,
                "limit": self.max_requests,
                "remaining": self.max_requests,
            }
        
        current = entry.get_count(self.window_seconds)
        return {
            "current": current,
            "limit": self.max_requests,
            "remaining": max(0, self.max_requests - current),
        }
    
    def reset(self, key: str) -> None:
        """
        Reset rate limit for a specific key.
        
        Args:
            key: Identifier to reset
        """
        with self._lock:
            if key in self._entries:
                del self._entries[key]
        logger.info("Rate limit reset", key=key)
    
    def reset_all(self) -> None:
        """Reset all rate limit entries."""
        with self._lock:
            self._entries.clear()
        logger.info("All rate limits reset")


# Global rate limiter instance
rate_limiter = RateLimiter()
