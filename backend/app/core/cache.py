"""Caching utilities for performance optimization."""
from functools import wraps
from typing import Any, Callable, Optional
import hashlib
import json
import time

# Simple in-memory cache (use Redis in production)
_cache: dict = {}
_cache_ttl: dict = {}


def cache_result(ttl_seconds: int = 300, key_prefix: str = ""):
    """
    Cache function results.
    
    Args:
        ttl_seconds: Time to live in seconds
        key_prefix: Prefix for cache keys
    
    Note: This is a simple in-memory implementation.
    For production, use Redis-based caching.
    """
    def decorator(func: Callable):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = _generate_cache_key(key_prefix, func.__name__, args, kwargs)
            
            # Check cache
            if cache_key in _cache:
                if time.time() < _cache_ttl.get(cache_key, 0):
                    return _cache[cache_key]
                else:
                    # Expired, remove it
                    del _cache[cache_key]
                    del _cache_ttl[cache_key]
            
            # Call function
            result = await func(*args, **kwargs)
            
            # Store in cache
            _cache[cache_key] = result
            _cache_ttl[cache_key] = time.time() + ttl_seconds
            
            return result
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = _generate_cache_key(key_prefix, func.__name__, args, kwargs)
            
            # Check cache
            if cache_key in _cache:
                if time.time() < _cache_ttl.get(cache_key, 0):
                    return _cache[cache_key]
                else:
                    # Expired, remove it
                    del _cache[cache_key]
                    del _cache_ttl[cache_key]
            
            # Call function
            result = func(*args, **kwargs)
            
            # Store in cache
            _cache[cache_key] = result
            _cache_ttl[cache_key] = time.time() + ttl_seconds
            
            return result
        
        # Return appropriate wrapper based on function type
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


def _generate_cache_key(prefix: str, func_name: str, args: tuple, kwargs: dict) -> str:
    """Generate a cache key from function arguments."""
    # Create a hash of the arguments
    key_data = {
        "prefix": prefix,
        "func": func_name,
        "args": str(args),
        "kwargs": json.dumps(kwargs, sort_keys=True),
    }
    key_string = json.dumps(key_data, sort_keys=True)
    key_hash = hashlib.md5(key_string.encode()).hexdigest()
    return f"{prefix}:{func_name}:{key_hash}" if prefix else f"{func_name}:{key_hash}"


def clear_cache(pattern: Optional[str] = None):
    """
    Clear cache entries.
    
    Args:
        pattern: Optional pattern to match cache keys. If None, clears all.
    """
    if pattern:
        keys_to_delete = [k for k in _cache.keys() if pattern in k]
        for key in keys_to_delete:
            _cache.pop(key, None)
            _cache_ttl.pop(key, None)
    else:
        _cache.clear()
        _cache_ttl.clear()

