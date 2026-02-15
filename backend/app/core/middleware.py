"""
Production middleware for security and monitoring.
"""

import time
import logging
from typing import Callable, Optional
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR, HTTP_429_TOO_MANY_REQUESTS

try:
    import sentry_sdk
    from sentry_sdk.integrations.fastapi import FastApiIntegration
    from sentry_sdk.integrations.starlette import StarletteIntegration
    from sentry_sdk.integrations.redis import RedisIntegration
    from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
    SENTRY_AVAILABLE = True
except ImportError:
    SENTRY_AVAILABLE = False

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log all requests with timing information."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        
        # Log request
        logger.info(f"Request: {request.method} {request.url.path}")
        
        try:
            response = await call_next(request)
            
            # Calculate duration
            duration = time.time() - start_time
            
            # Log response
            logger.info(
                f"Response: {request.method} {request.url.path} "
                f"- Status: {response.status_code} "
                f"- Duration: {duration:.3f}s"
            )
            
            # Add custom headers
            response.headers["X-Process-Time"] = str(duration)
            
            return response
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(
                f"Error: {request.method} {request.url.path} "
                f"- Duration: {duration:.3f}s - Error: {str(e)}"
            )
            raise


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """Global error handler for production with Sentry integration."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        try:
            return await call_next(request)
        except Exception as e:
            logger.exception(f"Unhandled error in {request.url.path}")
            
            # Capture exception in Sentry if available
            if SENTRY_AVAILABLE:
                with sentry_sdk.push_scope() as scope:
                    scope.set_context("request", {
                        "url": str(request.url),
                        "method": request.method,
                        "headers": dict(request.headers),
                        "client": request.client.host if request.client else "unknown",
                    })
                    sentry_sdk.capture_exception(e)
            
            # Return generic error in production
            return JSONResponse(
                status_code=HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "error": "Internal Server Error",
                    "message": "An unexpected error occurred. Please try again later.",
                    "path": str(request.url.path),
                }
            )


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        return response


# Redis-based rate limiting
import redis.asyncio as aioredis

class RedisRateLimiter:
    """Redis-backed distributed rate limiter."""
    
    def __init__(self, redis_client: aioredis.Redis, requests_per_minute: int = 60):
        self.redis = redis_client
        self.requests_per_minute = requests_per_minute
        self.window_seconds = 60
        
    async def is_allowed(self, client_ip: str) -> bool:
        """Check if request is allowed using sliding window."""
        try:
            key = f"rate_limit:{client_ip}"
            
            # Use Redis pipeline for atomic operations
            pipe = self.redis.pipeline()
            pipe.incr(key)
            pipe.expire(key, self.window_seconds)
            results = await pipe.execute()
            
            current_requests = results[0]
            
            return current_requests <= self.requests_per_minute
            
        except Exception as e:
            logger.error(f"Redis rate limiter error: {e}")
            # Fail open - allow request if Redis is down
            return True


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware using Redis."""
    
    def __init__(self, app, redis_client: aioredis.Redis, requests_per_minute: int = 60):
        super().__init__(app)
        self.rate_limiter = RedisRateLimiter(redis_client, requests_per_minute)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip rate limiting for health checks
        if request.url.path in ["/health", "/docs", "/redoc", "/openapi.json"]:
            return await call_next(request)
        
        # Get client IP (handle proxies)
        client_ip = request.headers.get("X-Forwarded-For", "").split(",")[0].strip()
        if not client_ip:
            client_ip = request.client.host if request.client else "unknown"
        
        # Check rate limit
        if not await self.rate_limiter.is_allowed(client_ip):
            logger.warning(f"Rate limit exceeded for {client_ip}")
            return JSONResponse(
                status_code=HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "error": "Too Many Requests",
                    "message": "Rate limit exceeded. Please try again later.",
                    "retry_after": 60
                },
                headers={"Retry-After": "60"}
            )
        
        return await call_next(request)


# Sentry initialization helper
def init_sentry(
    dsn: Optional[str] = None,
    environment: str = "production",
    traces_sample_rate: float = 0.1,
    profiles_sample_rate: float = 0.1,
    enable_tracing: bool = True,
) -> None:
    """Initialize Sentry SDK with FastAPI integrations.
    
    Args:
        dsn: Sentry DSN URL (required for Sentry to work)
        environment: Environment name (production, staging, development)
        traces_sample_rate: Percentage of transactions to trace (0.0 - 1.0)
        profiles_sample_rate: Percentage of transactions to profile (0.0 - 1.0)
        enable_tracing: Enable performance monitoring
    """
    if not SENTRY_AVAILABLE:
        logger.warning("Sentry SDK not installed. Install with: pip install sentry-sdk")
        return
    
    if not dsn:
        logger.info("Sentry DSN not provided. Error tracking disabled.")
        return
    
    try:
        sentry_sdk.init(
            dsn=dsn,
            environment=environment,
            integrations=[
                FastApiIntegration(transaction_style="url"),
                StarletteIntegration(transaction_style="url"),
                RedisIntegration(),
                SqlalchemyIntegration(),
            ],
            # Performance monitoring
            traces_sample_rate=traces_sample_rate if enable_tracing else 0.0,
            profiles_sample_rate=profiles_sample_rate if enable_tracing else 0.0,
            
            # Error filtering
            before_send=_before_send,
            
            # Additional options
            send_default_pii=False,  # Don't send personally identifiable information
            max_breadcrumbs=50,
            attach_stacktrace=True,
        )
        
        logger.info(f"Sentry initialized successfully for environment: {environment}")
        
    except Exception as e:
        logger.error(f"Failed to initialize Sentry: {e}")


def _before_send(event, hint):
    """Filter events before sending to Sentry."""
    # Filter out specific exceptions if needed
    if "exc_info" in hint:
        exc_type, exc_value, tb = hint["exc_info"]
        
        # Skip common/expected errors
        if exc_type.__name__ in ["KeyboardInterrupt", "SystemExit"]:
            return None
    
    return event
