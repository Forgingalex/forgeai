"""Rate limiting utilities."""
from functools import wraps
from typing import Callable
from fastapi import Request, HTTPException, status
from app.core.config import settings
import time
from collections import defaultdict

# In-memory rate limit store (use Redis in production)
_rate_limit_store: dict = defaultdict(list)


def rate_limit(max_requests: int = 60, window_seconds: int = 60):
    """
    Rate limiting decorator.
    
    Args:
        max_requests: Maximum number of requests allowed
        window_seconds: Time window in seconds
    
    Note: This is a simple in-memory implementation.
    For production, use Redis-based rate limiting.
    
    Why TF-IDF over embeddings for RAG:
    - Simpler implementation, no external vector DB needed
    - Good enough for small-medium knowledge bases
    - Lower computational overhead
    - Easier to debug and understand
    - Can be upgraded to embeddings later if needed
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            # Get client identifier (IP address)
            client_id = request.client.host if request.client else "unknown"
            
            # Get current time
            now = time.time()
            
            # Clean old entries
            _rate_limit_store[client_id] = [
                timestamp
                for timestamp in _rate_limit_store[client_id]
                if now - timestamp < window_seconds
            ]
            
            # Check rate limit
            if len(_rate_limit_store[client_id]) >= max_requests:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Rate limit exceeded: {max_requests} requests per {window_seconds} seconds",
                )
            
            # Add current request
            _rate_limit_store[client_id].append(now)
            
            return await func(request, *args, **kwargs)
        return wrapper
    return decorator

