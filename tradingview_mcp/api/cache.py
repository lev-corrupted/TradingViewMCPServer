"""Simple in-memory cache with TTL and LRU eviction support."""

import time
import logging
from typing import Optional, Any, Dict
from dataclasses import dataclass
from collections import OrderedDict

logger = logging.getLogger(__name__)


@dataclass
class CacheEntry:
    """Cache entry with value and expiration time."""
    value: Any
    expires_at: float


class ResponseCache:
    """
    In-memory cache with TTL (Time To Live) and LRU eviction.

    This cache helps reduce API calls by storing responses temporarily.
    When cache reaches max_size, least recently used entries are evicted.
    """

    def __init__(self, max_size: int = 1000):
        """
        Initialize cache with maximum size limit.

        Args:
            max_size: Maximum number of entries (default: 1000)
        """
        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._max_size = max_size
        self._hits = 0
        self._misses = 0
        self._evictions = 0

    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache if not expired.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found/expired
        """
        if key not in self._cache:
            self._misses += 1
            logger.debug(f"Cache miss: {key}")
            return None

        entry = self._cache[key]
        current_time = time.time()

        if current_time > entry.expires_at:
            # Entry expired, remove it
            del self._cache[key]
            self._misses += 1
            logger.debug(f"Cache expired: {key}")
            return None

        # Move to end to mark as recently used (LRU)
        self._cache.move_to_end(key)
        self._hits += 1
        logger.debug(f"Cache hit: {key}")
        return entry.value

    def set(self, key: str, value: Any, ttl: int) -> None:
        """
        Store value in cache with TTL. Evicts LRU entry if at capacity.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds
        """
        # Evict oldest entries if at capacity and key is new
        if key not in self._cache and len(self._cache) >= self._max_size:
            evicted_key, _ = self._cache.popitem(last=False)
            self._evictions += 1
            logger.debug(f"Cache evicted LRU entry: {evicted_key}")

        expires_at = time.time() + ttl
        self._cache[key] = CacheEntry(value=value, expires_at=expires_at)
        self._cache.move_to_end(key)  # Mark as recently used
        logger.debug(f"Cache set: {key} (TTL: {ttl}s)")

    def invalidate(self, key: str) -> None:
        """
        Remove a specific key from cache.

        Args:
            key: Cache key to remove
        """
        if key in self._cache:
            del self._cache[key]
            logger.debug(f"Cache invalidated: {key}")

    def clear(self) -> None:
        """Clear all cache entries."""
        self._cache.clear()
        logger.info("Cache cleared")

    def cleanup_expired(self) -> int:
        """
        Remove all expired entries from cache.

        Returns:
            Number of entries removed
        """
        current_time = time.time()
        expired_keys = [
            key for key, entry in self._cache.items()
            if current_time > entry.expires_at
        ]

        for key in expired_keys:
            del self._cache[key]

        if expired_keys:
            logger.debug(f"Cleaned up {len(expired_keys)} expired cache entries")

        return len(expired_keys)

    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.

        Returns:
            Dictionary with cache statistics
        """
        total = self._hits + self._misses
        hit_rate = (self._hits / total * 100) if total > 0 else 0

        return {
            "size": len(self._cache),
            "max_size": self._max_size,
            "hits": self._hits,
            "misses": self._misses,
            "evictions": self._evictions,
            "hit_rate": f"{hit_rate:.1f}%",
            "utilization": f"{len(self._cache) / self._max_size * 100:.1f}%"
        }
