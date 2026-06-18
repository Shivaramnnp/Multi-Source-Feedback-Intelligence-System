"""
Dependency injection utilities.

Re-exports commonly used dependencies for API route handlers.
"""

from app.auth.router import get_current_user
from app.database import get_db

__all__ = ["get_db", "get_current_user"]
