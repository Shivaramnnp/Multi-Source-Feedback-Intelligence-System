"""
Request and response logging middleware.

Logs request method, path, client ip, status code, and processing time.
"""

import logging
import time

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("app.middleware.logging")


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log details of every incoming request and outgoing response."""

    async def dispatch(self, request: Request, call_next):
        start_time = time.perf_counter()
        
        # Log incoming request
        client_host = request.client.host if request.client else "unknown"
        logger.info(
            "Incoming request: method=%s path=%s client=%s",
            request.method,
            request.url.path,
            client_host,
        )

        try:
            response = await call_next(request)
            process_time = (time.perf_counter() - start_time) * 1000
            
            # Log successful response
            logger.info(
                "Completed request: method=%s path=%s status_code=%d duration=%.2fms",
                request.method,
                request.url.path,
                response.status_code,
                process_time,
            )
            return response
        except Exception as e:
            process_time = (time.perf_counter() - start_time) * 1000
            logger.error(
                "Failed request: method=%s path=%s error=%s duration=%.2fms",
                request.method,
                request.url.path,
                str(e),
                process_time,
            )
            raise e
