"""
Middleware package init.
"""

from app.middleware.logging import LoggingMiddleware

__all__ = ["LoggingMiddleware"]
