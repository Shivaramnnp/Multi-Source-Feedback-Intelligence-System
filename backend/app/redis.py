"""
Redis connection manager and utility functions.
"""

import logging
from redis.asyncio import Redis, from_url

from app.config import get_settings

logger = logging.getLogger("app.redis")
settings = get_settings()

_redis_client: Redis | None = None


def get_redis_client() -> Redis:
    """Get the global Redis client instance, initializing it if necessary."""
    global _redis_client
    if _redis_client is None:
        _redis_client = from_url(settings.REDIS_URL, decode_responses=True)
        logger.info("Redis client initialized at %s", settings.REDIS_URL)
    return _redis_client


async def close_redis() -> None:
    """Close the Redis connection if it is open."""
    global _redis_client
    if _redis_client is not None:
        await _redis_client.close()
        _redis_client = None
        logger.info("Redis client closed.")


async def ping_redis() -> bool:
    """Ping Redis to check if connection is active."""
    try:
        client = get_redis_client()
        await client.ping()
        return True
    except Exception as e:
        logger.error("Redis ping failed: %s", str(e))
        return False
