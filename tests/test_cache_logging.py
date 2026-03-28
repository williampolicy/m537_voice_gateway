"""
M537 Voice Gateway - Cache and Logging Tests
Tests for cache optimization and logging configuration
"""
import pytest
import sys
import os
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))


class TestQueryCache:
    """Tests for QueryCache"""

    @pytest.fixture
    def cache(self):
        from services.cache import QueryCache
        return QueryCache(max_size=10)

    def test_cache_set_and_get(self, cache):
        """Test basic cache operations"""
        cache.set("test_intent", {"key": "value"}, {"result": "data"})
        result = cache.get("test_intent", {"key": "value"})
        assert result == {"result": "data"}

    def test_cache_miss(self, cache):
        """Test cache miss returns None"""
        result = cache.get("nonexistent", {})
        assert result is None

    def test_cache_expiration(self, cache):
        """Test cache entries expire"""
        from datetime import timedelta
        cache.set("expire_test", {}, {"data": "test"})

        # Manually expire entry
        key = cache._make_key("expire_test", {})
        cache.cache[key].ttl = timedelta(seconds=-1)

        result = cache.get("expire_test", {})
        assert result is None

    def test_cache_lru_eviction(self, cache):
        """Test LRU eviction when at capacity"""
        # Fill cache beyond capacity
        for i in range(15):
            cache.set(f"intent_{i}", {}, {"value": i})

        # Cache should not exceed max_size
        assert len(cache.cache) <= cache.max_size

    def test_cache_stats(self, cache):
        """Test cache statistics"""
        cache.set("stats_test", {}, {"data": "test"})
        cache.get("stats_test", {})
        cache.get("nonexistent", {})

        stats = cache.get_stats()
        assert "size" in stats
        assert "hits" in stats
        assert "misses" in stats
        assert "hit_rate" in stats
        assert "memory_kb" in stats

    def test_cache_hot_entries(self, cache):
        """Test getting hot entries"""
        cache.set("hot_intent", {}, {"data": "test"})
        for _ in range(5):
            cache.get("hot_intent", {})

        hot = cache.get_hot_entries(limit=5)
        assert len(hot) > 0
        assert hot[0]["hits"] >= 5

    def test_cache_invalidation(self, cache):
        """Test cache invalidation"""
        cache.set("invalidate_me", {}, {"data": "test"})
        assert cache.get("invalidate_me", {}) is not None

        cache.invalidate("invalidate_me")
        assert cache.get("invalidate_me", {}) is None

    def test_cache_clear_all(self, cache):
        """Test clearing entire cache"""
        for i in range(5):
            cache.set(f"clear_{i}", {}, {"value": i})

        cache.invalidate()
        assert len(cache.cache) == 0

    def test_cache_cleanup_expired(self, cache):
        """Test cleanup of expired entries"""
        from datetime import timedelta

        cache.set("fresh", {}, {"data": "fresh"})
        cache.set("stale", {}, {"data": "stale"})

        # Expire one entry
        key = cache._make_key("stale", {})
        cache.cache[key].ttl = timedelta(seconds=-1)

        cache.cleanup_expired()

        assert cache.get("fresh", {}) is not None
        assert "stale" not in str(cache.cache.keys())

    def test_cache_warm(self, cache):
        """Test cache warming"""
        entries = [
            {"intent": "warm1", "params": {}, "data": {"value": 1}},
            {"intent": "warm2", "params": {}, "data": {"value": 2}},
        ]
        cache.warm(entries)

        assert cache.get("warm1", {}) == {"value": 1}
        assert cache.get("warm2", {}) == {"value": 2}

    def test_cache_ttl_config(self, cache):
        """Test TTL configuration by intent type"""
        from services.cache import QueryCache

        # Check that different intents have different TTLs
        assert QueryCache.TTL_CONFIG["count_projects"] > QueryCache.TTL_CONFIG["system_status"]
        assert QueryCache.TTL_CONFIG["project_summary"] >= 600


class TestLoggingConfig:
    """Tests for logging configuration"""

    def test_setup_logging(self):
        """Test logging setup"""
        with tempfile.TemporaryDirectory() as tmpdir:
            from logging_config import setup_logging
            logger = setup_logging(log_dir=tmpdir, log_level="DEBUG")
            assert logger is not None

    def test_access_logger(self):
        """Test access logger exists"""
        from logging_config import get_access_logger
        logger = get_access_logger()
        assert logger is not None
        assert logger.name == "m537.access"

    def test_log_request(self):
        """Test request logging function"""
        from logging_config import log_request
        # Should not raise
        log_request("GET", "/api/health", 200, 15.5, "127.0.0.1")

    def test_log_files_created(self):
        """Test log files are created"""
        with tempfile.TemporaryDirectory() as tmpdir:
            from logging_config import setup_logging
            setup_logging(log_dir=tmpdir)

            import logging
            logging.info("Test message")

            # Check log files exist
            assert os.path.exists(os.path.join(tmpdir, "m537_gateway.log"))


class TestCacheIntegration:
    """Integration tests for cache with query service"""

    def test_cache_with_intent_parser(self):
        """Test cache integration with intent parser"""
        from services.cache import query_cache

        # Simulate caching a query result
        query_cache.set(
            "count_projects",
            {},
            {"count": 10, "source": "cached"}
        )

        result = query_cache.get("count_projects", {})
        assert result is not None
        assert result["source"] == "cached"


# Run tests with: pytest tests/test_cache_logging.py -v
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
