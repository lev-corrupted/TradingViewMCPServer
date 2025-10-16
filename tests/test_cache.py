"""Tests for caching functionality."""

import time
import pytest
from tradingview_mcp.api.cache import ResponseCache


def test_cache_set_and_get():
    """Test basic cache set and get operations."""
    cache = ResponseCache()

    cache.set("test_key", "test_value", ttl=60)
    assert cache.get("test_key") == "test_value"


def test_cache_miss():
    """Test cache miss returns None."""
    cache = ResponseCache()
    assert cache.get("nonexistent_key") is None


def test_cache_expiration():
    """Test that cache entries expire after TTL."""
    cache = ResponseCache()

    cache.set("expire_key", "expire_value", ttl=1)
    assert cache.get("expire_key") == "expire_value"

    # Wait for expiration
    time.sleep(1.1)
    assert cache.get("expire_key") is None


def test_cache_invalidate():
    """Test cache invalidation."""
    cache = ResponseCache()

    cache.set("key", "value", ttl=60)
    assert cache.get("key") == "value"

    cache.invalidate("key")
    assert cache.get("key") is None


def test_cache_clear():
    """Test clearing entire cache."""
    cache = ResponseCache()

    cache.set("key1", "value1", ttl=60)
    cache.set("key2", "value2", ttl=60)

    cache.clear()

    assert cache.get("key1") is None
    assert cache.get("key2") is None


def test_cache_stats():
    """Test cache statistics."""
    cache = ResponseCache()

    # Generate some hits and misses
    cache.set("key", "value", ttl=60)
    cache.get("key")  # Hit
    cache.get("key")  # Hit
    cache.get("nonexistent")  # Miss

    stats = cache.get_stats()

    assert stats["hits"] == 2
    assert stats["misses"] == 1
    assert stats["size"] == 1


def test_cache_cleanup():
    """Test cleanup of expired entries."""
    cache = ResponseCache()

    cache.set("key1", "value1", ttl=1)
    cache.set("key2", "value2", ttl=60)

    time.sleep(1.1)

    removed = cache.cleanup_expired()

    assert removed == 1
    assert cache.get("key1") is None
    assert cache.get("key2") == "value2"
