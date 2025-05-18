"""Rate limiting middleware using SlowAPI."""
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request
from app.core.redis_client import redis_client


def get_client_ip(request: Request) -> str:
    """Get client IP address for rate limiting."""
    # Check for X-Forwarded-For header (proxy/load balancer)
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    
    # Check for X-Real-IP header
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    
    # Fall back to direct client IP
    if request.client:
        return request.client.host
    
    return "unknown"


# Initialize rate limiter with Redis backend
limiter = Limiter(
    key_func=get_client_ip,
    storage_uri=None,  # Will use in-memory if Redis unavailable
    default_limits=["200 per day", "50 per hour"]
)


# Custom rate limit configurations for different endpoint types
class RateLimits:
    """Rate limit configurations."""
    # These limits are pretty conservative - adjust based on your traffic
    # We started more generous but had to tighten up after some abuse
    
    # Authentication endpoints - stricter limits
    AUTH = "5 per minute"
    LOGIN = "5 per minute"  # Might be too strict? Monitor this
    REGISTER = "3 per hour"
    
    # API endpoints - moderate limits
    API_READ = "100 per minute"
    API_WRITE = "30 per minute"
    
    # Analytics endpoints - relaxed limits
    ANALYTICS = "60 per minute"
    
    # Export endpoints - strict limits
    EXPORT = "10 per hour"
