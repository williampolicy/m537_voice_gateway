"""
M537 Voice Gateway - Analytics
Usage analytics and metrics aggregation
"""
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional
from collections import defaultdict
from dataclasses import dataclass, field
import threading

logger = logging.getLogger(__name__)


@dataclass
class QueryMetric:
    """Single query metric entry"""
    timestamp: datetime
    intent: str
    confidence: float
    duration_ms: float
    success: bool
    language: str
    cached: bool = False
    tool_used: Optional[str] = None


class AnalyticsCollector:
    """
    Collects and aggregates usage analytics.
    Provides insights for dashboards and reporting.
    """

    def __init__(self, retention_hours: int = 24):
        self.retention_hours = retention_hours
        self._metrics: List[QueryMetric] = []
        self._intent_counts: Dict[str, int] = defaultdict(int)
        self._language_counts: Dict[str, int] = defaultdict(int)
        self._hourly_counts: Dict[str, int] = defaultdict(int)
        self._lock = threading.Lock()

        # Error tracking
        self._error_counts: Dict[str, int] = defaultdict(int)

        # Performance tracking
        self._duration_samples: List[float] = []
        self._max_samples = 1000

    def record_query(
        self,
        intent: str,
        confidence: float,
        duration_ms: float,
        success: bool,
        language: str = "zh-CN",
        cached: bool = False,
        tool_used: Optional[str] = None,
        error_code: Optional[str] = None
    ):
        """Record a query metric"""
        now = datetime.now(timezone.utc)

        metric = QueryMetric(
            timestamp=now,
            intent=intent,
            confidence=confidence,
            duration_ms=duration_ms,
            success=success,
            language=language,
            cached=cached,
            tool_used=tool_used
        )

        with self._lock:
            self._metrics.append(metric)
            self._intent_counts[intent] += 1
            self._language_counts[language] += 1

            # Hourly bucket
            hour_key = now.strftime("%Y-%m-%d %H:00")
            self._hourly_counts[hour_key] += 1

            # Track errors
            if not success and error_code:
                self._error_counts[error_code] += 1

            # Track performance
            self._duration_samples.append(duration_ms)
            if len(self._duration_samples) > self._max_samples:
                self._duration_samples = self._duration_samples[-self._max_samples:]

            # Cleanup old metrics
            self._cleanup_old_metrics()

    def _cleanup_old_metrics(self):
        """Remove metrics older than retention period"""
        cutoff = datetime.now(timezone.utc) - timedelta(hours=self.retention_hours)
        self._metrics = [m for m in self._metrics if m.timestamp > cutoff]

    def get_summary(self) -> Dict[str, Any]:
        """Get analytics summary"""
        with self._lock:
            if not self._metrics:
                return {
                    "total_queries": 0,
                    "period_hours": self.retention_hours,
                    "message": "No data available"
                }

            total = len(self._metrics)
            successful = sum(1 for m in self._metrics if m.success)
            cached = sum(1 for m in self._metrics if m.cached)

            # Calculate percentiles
            durations = sorted([m.duration_ms for m in self._metrics])
            p50 = durations[len(durations) // 2] if durations else 0
            p95 = durations[int(len(durations) * 0.95)] if durations else 0
            p99 = durations[int(len(durations) * 0.99)] if durations else 0

            return {
                "period_hours": self.retention_hours,
                "total_queries": total,
                "successful_queries": successful,
                "failed_queries": total - successful,
                "success_rate": round(successful / total * 100, 2) if total > 0 else 0,
                "cached_responses": cached,
                "cache_hit_rate": round(cached / total * 100, 2) if total > 0 else 0,
                "performance": {
                    "avg_duration_ms": round(sum(durations) / len(durations), 2) if durations else 0,
                    "p50_duration_ms": round(p50, 2),
                    "p95_duration_ms": round(p95, 2),
                    "p99_duration_ms": round(p99, 2)
                },
                "top_intents": self._get_top_items(self._intent_counts, 10),
                "languages": dict(self._language_counts),
                "generated_at": datetime.now(timezone.utc).isoformat()
            }

    def _get_top_items(self, counts: Dict[str, int], limit: int) -> List[Dict]:
        """Get top N items from a count dict"""
        sorted_items = sorted(counts.items(), key=lambda x: x[1], reverse=True)
        return [{"name": k, "count": v} for k, v in sorted_items[:limit]]

    def get_hourly_trend(self, hours: int = 24) -> List[Dict]:
        """Get hourly query trend"""
        with self._lock:
            now = datetime.now(timezone.utc)
            result = []

            for i in range(hours):
                hour = now - timedelta(hours=i)
                hour_key = hour.strftime("%Y-%m-%d %H:00")
                count = self._hourly_counts.get(hour_key, 0)
                result.append({
                    "hour": hour_key,
                    "count": count
                })

            return list(reversed(result))

    def get_intent_breakdown(self) -> Dict[str, Any]:
        """Get detailed intent breakdown"""
        with self._lock:
            total = sum(self._intent_counts.values())

            return {
                "total_intents": len(self._intent_counts),
                "breakdown": [
                    {
                        "intent": intent,
                        "count": count,
                        "percentage": round(count / total * 100, 2) if total > 0 else 0
                    }
                    for intent, count in sorted(
                        self._intent_counts.items(),
                        key=lambda x: x[1],
                        reverse=True
                    )
                ]
            }

    def get_error_breakdown(self) -> Dict[str, Any]:
        """Get error breakdown"""
        with self._lock:
            total = sum(self._error_counts.values())

            return {
                "total_errors": total,
                "breakdown": [
                    {"error_code": code, "count": count}
                    for code, count in sorted(
                        self._error_counts.items(),
                        key=lambda x: x[1],
                        reverse=True
                    )
                ]
            }

    def get_performance_stats(self) -> Dict[str, Any]:
        """Get detailed performance statistics"""
        with self._lock:
            if not self._duration_samples:
                return {"message": "No performance data"}

            samples = sorted(self._duration_samples)
            n = len(samples)

            return {
                "sample_count": n,
                "min_ms": round(min(samples), 2),
                "max_ms": round(max(samples), 2),
                "avg_ms": round(sum(samples) / n, 2),
                "median_ms": round(samples[n // 2], 2),
                "p75_ms": round(samples[int(n * 0.75)], 2),
                "p90_ms": round(samples[int(n * 0.90)], 2),
                "p95_ms": round(samples[int(n * 0.95)], 2),
                "p99_ms": round(samples[int(n * 0.99)], 2)
            }

    def reset(self):
        """Reset all analytics data"""
        with self._lock:
            self._metrics.clear()
            self._intent_counts.clear()
            self._language_counts.clear()
            self._hourly_counts.clear()
            self._error_counts.clear()
            self._duration_samples.clear()
            logger.info("Analytics data reset")


# Global analytics instance
analytics = AnalyticsCollector()


def record_query_metric(
    intent: str,
    confidence: float,
    duration_ms: float,
    success: bool,
    **kwargs
):
    """Convenience function to record a query metric"""
    analytics.record_query(intent, confidence, duration_ms, success, **kwargs)
