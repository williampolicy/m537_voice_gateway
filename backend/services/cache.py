"""
M537 Voice Gateway - Query Cache
In-memory caching with LRU eviction and memory monitoring
"""
from typing import Dict, Any, Optional, Tuple, Callable
from datetime import datetime, timezone, timedelta
from collections import OrderedDict
import threading
import hashlib
import logging
import sys

logger = logging.getLogger(__name__)


class CacheEntry:
    """Represents a cached query result"""

    def __init__(self, data: Dict[str, Any], ttl_seconds: int = 60):
        self.data = data
        self.created_at = datetime.now(timezone.utc)
        self.ttl = timedelta(seconds=ttl_seconds)
        self.hits = 0

    def is_expired(self) -> bool:
        return datetime.now(timezone.utc) - self.created_at > self.ttl

    def hit(self) -> Dict[str, Any]:
        self.hits += 1
        return self.data


class QueryCache:
    """
    LRU cache for query results.
    Different TTLs for different query types based on data volatility.
    """

    # Cache TTL by intent (seconds)
    TTL_CONFIG = {
        # Static data - longer TTL
        "count_projects": 300,      # 5 minutes
        "missing_readme": 300,      # 5 minutes
        "project_summary": 600,     # 10 minutes
        "cron_jobs": 300,           # 5 minutes

        # Semi-dynamic data - medium TTL
        "list_ports": 60,           # 1 minute
        "list_containers": 60,      # 1 minute
        "list_tmux": 60,            # 1 minute
        "recent_updates": 120,      # 2 minutes
        "git_status": 60,           # 1 minute
        "disk_usage": 60,           # 1 minute

        # Dynamic data - short TTL
        "system_status": 30,        # 30 seconds
        "recent_errors": 30,        # 30 seconds
        "p0_health": 30,            # 30 seconds
        "uptime_info": 30,          # 30 seconds
        "process_list": 30,         # 30 seconds
        "network_info": 30,         # 30 seconds
        "service_logs": 15,         # 15 seconds (very dynamic)
    }

    def __init__(self, max_size: int = 500):
        self.cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self.max_size = max_size
        self._lock = threading.Lock()

        # Stats
        self.hits = 0
        self.misses = 0

    def _make_key(self, intent: str, params: Dict[str, Any]) -> str:
        """Generate cache key from intent and params"""
        param_str = str(sorted(params.items())) if params else ""
        key_data = f"{intent}:{param_str}"
        return hashlib.md5(key_data.encode()).hexdigest()

    def get(self, intent: str, params: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """Get cached result if available and not expired"""
        params = params or {}
        key = self._make_key(intent, params)

        with self._lock:
            if key not in self.cache:
                self.misses += 1
                return None

            entry = self.cache[key]

            if entry.is_expired():
                del self.cache[key]
                self.misses += 1
                logger.debug(f"Cache expired for {intent}")
                return None

            # Move to end (LRU)
            self.cache.move_to_end(key)
            self.hits += 1

            logger.debug(f"Cache hit for {intent} (hits: {entry.hits})")
            return entry.hit()

    def set(self, intent: str, params: Dict[str, Any], data: Dict[str, Any]):
        """Cache query result"""
        params = params or {}
        key = self._make_key(intent, params)
        ttl = self.TTL_CONFIG.get(intent, 60)

        with self._lock:
            # Remove oldest if at capacity
            while len(self.cache) >= self.max_size:
                self.cache.popitem(last=False)

            self.cache[key] = CacheEntry(data, ttl)
            logger.debug(f"Cached {intent} with TTL {ttl}s")

    def clear(self):
        """Clear all cache entries"""
        self.invalidate()
        # Reset stats
        with self._lock:
            self.hits = 0
            self.misses = 0

    def invalidate(self, intent: str = None, params: Dict[str, Any] = None):
        """Invalidate cache entries"""
        with self._lock:
            if intent is None:
                # Clear all
                self.cache.clear()
                logger.info("Cache cleared")
                return

            if params:
                # Invalidate specific entry
                key = self._make_key(intent, params)
                if key in self.cache:
                    del self.cache[key]
            else:
                # Invalidate all entries for this intent
                to_remove = [
                    k for k in self.cache.keys()
                    if k.startswith(self._make_key(intent, {}))
                ]
                for k in to_remove:
                    del self.cache[k]

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self._lock:
            total = self.hits + self.misses
            hit_rate = (self.hits / total * 100) if total > 0 else 0

            # Calculate memory usage
            memory_bytes = sum(
                sys.getsizeof(k) + sys.getsizeof(v.data)
                for k, v in self.cache.items()
            )

            return {
                "size": len(self.cache),
                "max_size": self.max_size,
                "hits": self.hits,
                "misses": self.misses,
                "hit_rate": f"{hit_rate:.1f}%",
                "memory_bytes": memory_bytes,
                "memory_kb": round(memory_bytes / 1024, 2)
            }

    def get_hot_entries(self, limit: int = 10) -> list:
        """Get most frequently accessed cache entries"""
        with self._lock:
            entries = [
                {"key": k[:8], "hits": v.hits, "age_seconds": (datetime.now(timezone.utc) - v.created_at).seconds}
                for k, v in self.cache.items()
            ]
            return sorted(entries, key=lambda x: x["hits"], reverse=True)[:limit]

    def warm(self, entries: list):
        """Pre-warm cache with frequently accessed data"""
        for entry in entries:
            intent = entry.get("intent")
            params = entry.get("params", {})
            data = entry.get("data")
            if intent and data:
                self.set(intent, params, data)
        logger.info(f"Cache warmed with {len(entries)} entries")

    def cleanup_expired(self):
        """Remove all expired entries"""
        with self._lock:
            expired = [
                k for k, v in self.cache.items()
                if v.is_expired()
            ]
            for k in expired:
                del self.cache[k]

            if expired:
                logger.debug(f"Cleaned up {len(expired)} expired cache entries")


# Global cache instance
query_cache = QueryCache()
