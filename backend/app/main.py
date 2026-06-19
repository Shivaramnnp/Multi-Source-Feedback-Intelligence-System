"""
FastAPI application entry point.

Configures CORS, middleware, global exception handlers, API routers,
and handles database initialization on startup.
"""

import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.ai_analysis import router as ai_analysis_router
from app.api.v1.feedback import router as feedback_router
from app.api.v1.intelligence import router as intelligence_router
from app.api.v1.agents import router as agents_router
from app.api.v1.benchmark import router as benchmark_router
from app.auth.router import router as auth_router

from app.config import get_settings
from app.database import create_tables
from app.exceptions.handlers import register_exception_handlers
from app.middleware.logging import LoggingMiddleware

# Configure logging
settings = get_settings()
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("app.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle events manager for database startup/shutdown."""
    logger.info("Starting up Feedback Intelligence System...")
    try:
        await create_tables()
        logger.info("Database tables initialized.")
    except Exception as e:
        logger.error("Error creating database tables: %s", str(e))
    yield
    logger.info("Shutting down Feedback Intelligence System...")
    from app.redis import close_redis
    await close_redis()


app = FastAPI(
    title="Feedback Intelligence System",
    description="Production-ready Feedback Intelligence System with AI analytics and auto-tagging.",
    version="1.0.0",
    lifespan=lifespan,
)

# Exception handlers
register_exception_handlers(app)

# Middlewares
app.add_middleware(LoggingMiddleware)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Routers
# Mount auth under /api/v1 and also /auth for flexibility
app.include_router(auth_router, prefix="/api/v1")
app.include_router(auth_router, prefix="/auth")

app.include_router(feedback_router, prefix="/api/v1")
app.include_router(intelligence_router, prefix="/api/v1")
app.include_router(ai_analysis_router, prefix="/api/v1")
app.include_router(agents_router, prefix="/api/v1")
app.include_router(benchmark_router, prefix="/api/v1")



@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "Feedback Intelligence System"}


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
