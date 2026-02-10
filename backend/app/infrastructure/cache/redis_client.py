"""
Redis Cache Client
==================
Centralized Redis connection and caching utilities.
"""

import json
import redis
from typing import Optional, Any
from datetime import timedelta

from app.config import REDIS_HOST, REDIS_PORT, CACHE_TTL
from app.utils.logger import get_logger

logger = get_logger(__name__)


class RedisCache:
    """Redis cache wrapper with connection pooling."""
    
    def __init__(self):
        try:
            self.client = redis.Redis(
                host=REDIS_HOST,
                port=REDIS_PORT,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True,
                max_connections=50
            )
            self.client.ping()
            logger.info(f"✓ Redis connected: {REDIS_HOST}:{REDIS_PORT}")
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}. Caching disabled.")
            self.client = None
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if not self.client:
            return None
        
        try:
            value = self.client.get(key)
            if value:
                return json.loads(value)
        except Exception as e:
            logger.error(f"Redis GET error for key '{key}': {e}")
        
        return None
    
    def set(self, key: str, value: Any, ttl: int = CACHE_TTL) -> bool:
        """Set value in cache with TTL."""
        if not self.client:
            return False
        
        try:
            self.client.setex(
                key,
                timedelta(seconds=ttl),
                json.dumps(value)
            )
            return True
        except Exception as e:
            logger.error(f"Redis SET error for key '{key}': {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete key from cache."""
        if not self.client:
            return False
        
        try:
            self.client.delete(key)
            return True
        except Exception as e:
            logger.error(f"Redis DELETE error for key '{key}': {e}")
            return False
    
    def exists(self, key: str) -> bool:
        """Check if key exists."""
        if not self.client:
            return False
        
        try:
            return bool(self.client.exists(key))
        except Exception as e:
            logger.error(f"Redis EXISTS error for key '{key}': {e}")
            return False
    
    def clear_pattern(self, pattern: str) -> int:
        """Delete all keys matching pattern."""
        if not self.client:
            return 0
        
        try:
            keys = self.client.keys(pattern)
            if keys:
                return self.client.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Redis CLEAR error for pattern '{pattern}': {e}")
            return 0


# Singleton instance
_cache = None

def get_cache() -> RedisCache:
    """Get Redis cache instance (singleton)."""
    global _cache
    if _cache is None:
        _cache = RedisCache()
    return _cache
