"""Cache package - Redis integration."""

from .redis_client import get_cache, RedisCache

__all__ = ['get_cache', 'RedisCache']
