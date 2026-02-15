"""
F1 Race Replay — FastAPI Backend
Main application entry point.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from app.core.config import get_settings
from app.core.database import init_db
from app.core.middleware import (
    RequestLoggingMiddleware,
    ErrorHandlerMiddleware,
    SecurityHeadersMiddleware,
    RateLimitMiddleware,
    init_sentry,
)
from app.api.routes import seasons, races
from app.api.websocket import router as ws_router
import redis.asyncio as aioredis

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
)
logger = logging.getLogger(__name__)
settings = get_settings()

# Initialize Sentry
if settings.sentry_dsn:
    init_sentry(
        dsn=settings.sentry_dsn,
        environment=settings.sentry_environment,
        traces_sample_rate=settings.sentry_traces_sample_rate,
        profiles_sample_rate=settings.sentry_profiles_sample_rate,
        enable_tracing=not settings.debug,
    )

# Initialize Redis client for rate limiting
redis_client = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    global redis_client
    
    # Startup
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    await init_db()
    logger.info("Database initialized")
    
    # Initialize Redis
    try:
        redis_client = await aioredis.from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True,
        )
        await redis_client.ping()
        logger.info("Redis connected")
    except Exception as e:
        logger.warning(f"Redis connection failed: {e}. Rate limiting will be disabled.")
        redis_client = None
    
    yield
    
    # Shutdown
    logger.info("Shutting down...")
    if redis_client:
        await redis_client.close()
        logger.info("Redis connection closed")


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Interactive Formula 1 race replay and data visualization API",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Production middleware
if not settings.debug:
    # Error handler (catches all errors)
    app.add_middleware(ErrorHandlerMiddleware)
    
    # Rate limiting (only if Redis is available)
    if redis_client:
        app.add_middleware(
            RateLimitMiddleware,
            redis_client=redis_client,
            requests_per_minute=settings.rate_limit_per_minute,
        )
    
    # Security headers
    app.add_middleware(SecurityHeadersMiddleware)
    
    # Trusted host (prevent host header attacks)
    # Add your production domains
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["*"]  # Configure with your actual domains in production
    )

# Always enable these
app.add_middleware(GZipMiddleware, minimum_size=1000)  # Compress responses
app.add_middleware(RequestLoggingMiddleware)  # Log all requests

# Include routers
app.include_router(seasons.router, prefix="/api")
app.include_router(races.router, prefix="/api")
app.include_router(ws_router)


@app.get("/")
async def root():
    """Root endpoint with API info."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "docs": "/docs",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint with database and Redis connectivity check."""
    from app.core.database import async_session_maker
    from sqlalchemy import text
    
    health_status = {
        "status": "healthy",
        "version": settings.app_version,
        "environment": "development" if settings.debug else "production"
    }
    
    # Check database connectivity
    try:
        async with async_session_maker() as session:
            await session.execute(text("SELECT 1"))
        health_status["database"] = "connected"
    except Exception as e:
        health_status["database"] = "disconnected"
        health_status["status"] = "degraded"
        logger.error(f"Database health check failed: {e}")
    
    # Check Redis connectivity
    if redis_client:
        try:
            await redis_client.ping()
            health_status["redis"] = "connected"
        except Exception as e:
            health_status["redis"] = "disconnected"
            health_status["status"] = "degraded"
            logger.error(f"Redis health check failed: {e}")
    else:
        health_status["redis"] = "not_configured"
    
    return health_status


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )
