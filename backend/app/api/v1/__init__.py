# backend/app/api/v1/__init__.py
"""
API v1 package.

Export the main router for use in the application.
"""

from .router import router

__all__ = ["router"]
