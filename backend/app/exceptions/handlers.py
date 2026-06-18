"""
Global exception handlers for the FastAPI application.

Provides custom exception classes and handlers for consistent error responses.
"""

import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


class FeedbackNotFoundError(Exception):
    """Raised when a requested feedback entry does not exist."""

    def __init__(self, feedback_id: str) -> None:
        self.feedback_id = feedback_id
        super().__init__(f"Feedback with id '{feedback_id}' not found.")


class IntelligenceEngineError(Exception):
    """Raised when the intelligence engine processing fails."""

    def __init__(self, detail: str) -> None:
        self.detail = detail
        super().__init__(detail)


async def feedback_not_found_handler(request: Request, exc: FeedbackNotFoundError) -> JSONResponse:
    """Handle FeedbackNotFoundError with a 404 response."""
    return JSONResponse(
        status_code=404,
        content={
            "error": "not_found",
            "message": str(exc),
            "feedback_id": exc.feedback_id,
        },
    )


async def intelligence_engine_error_handler(request: Request, exc: IntelligenceEngineError) -> JSONResponse:
    """Handle IntelligenceEngineError with a 422 response."""
    logger.error("Intelligence engine error: %s", exc.detail)
    return JSONResponse(
        status_code=422,
        content={
            "error": "intelligence_engine_error",
            "message": exc.detail,
        },
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handle Pydantic/FastAPI validation errors with a structured 422 response."""
    errors = []
    for error in exc.errors():
        errors.append({
            "field": ".".join(str(loc) for loc in error.get("loc", [])),
            "message": error.get("msg", "Validation error"),
            "type": error.get("type", "unknown"),
        })
    return JSONResponse(
        status_code=422,
        content={"error": "validation_error", "details": errors},
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Catch-all handler for unhandled exceptions."""
    logger.exception("Unhandled exception on %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=500,
        content={
            "error": "internal_server_error",
            "message": "An unexpected error occurred. Please try again later.",
        },
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Register all custom exception handlers on the FastAPI app."""
    app.add_exception_handler(FeedbackNotFoundError, feedback_not_found_handler)
    app.add_exception_handler(IntelligenceEngineError, intelligence_engine_error_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)
