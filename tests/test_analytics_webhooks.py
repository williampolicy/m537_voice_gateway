"""
M537 Voice Gateway - Analytics and Webhooks Tests
Tests for usage analytics and webhook notifications
"""
import pytest
import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))


class TestAnalytics:
    """Tests for analytics collector"""

    @pytest.fixture
    def collector(self):
        from analytics import AnalyticsCollector
        return AnalyticsCollector(retention_hours=1)

    def test_record_query(self, collector):
        """Test recording a query metric"""
        collector.record_query(
            intent="count_projects",
            confidence=0.95,
            duration_ms=50.5,
            success=True,
            language="zh-CN"
        )

        summary = collector.get_summary()
        assert summary["total_queries"] == 1
        assert summary["successful_queries"] == 1

    def test_record_multiple_queries(self, collector):
        """Test recording multiple queries"""
        for i in range(10):
            collector.record_query(
                intent="test_intent",
                confidence=0.9,
                duration_ms=float(i * 10),
                success=i % 2 == 0,
                language="en-US"
            )

        summary = collector.get_summary()
        assert summary["total_queries"] == 10
        assert summary["successful_queries"] == 5

    def test_intent_counts(self, collector):
        """Test intent counting"""
        for _ in range(3):
            collector.record_query("intent_a", 0.9, 10, True)
        for _ in range(5):
            collector.record_query("intent_b", 0.9, 10, True)

        breakdown = collector.get_intent_breakdown()
        assert breakdown["total_intents"] == 2

        # intent_b should be first (more counts)
        assert breakdown["breakdown"][0]["intent"] == "intent_b"
        assert breakdown["breakdown"][0]["count"] == 5

    def test_language_counts(self, collector):
        """Test language counting"""
        collector.record_query("test", 0.9, 10, True, language="zh-CN")
        collector.record_query("test", 0.9, 10, True, language="en-US")
        collector.record_query("test", 0.9, 10, True, language="zh-CN")

        summary = collector.get_summary()
        assert summary["languages"]["zh-CN"] == 2
        assert summary["languages"]["en-US"] == 1

    def test_performance_stats(self, collector):
        """Test performance statistics"""
        durations = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
        for d in durations:
            collector.record_query("test", 0.9, d, True)

        stats = collector.get_performance_stats()
        assert stats["sample_count"] == 10
        assert stats["min_ms"] == 10
        assert stats["max_ms"] == 100
        assert stats["avg_ms"] == 55

    def test_hourly_trend(self, collector):
        """Test hourly trend"""
        collector.record_query("test", 0.9, 10, True)

        trend = collector.get_hourly_trend(hours=1)
        assert len(trend) == 1
        assert trend[0]["count"] >= 1

    def test_error_tracking(self, collector):
        """Test error tracking"""
        collector.record_query(
            "test", 0.5, 10, False,
            error_code="UNKNOWN_INTENT"
        )
        collector.record_query(
            "test", 0.5, 10, False,
            error_code="UNKNOWN_INTENT"
        )
        collector.record_query(
            "test", 0.5, 10, False,
            error_code="TOOL_ERROR"
        )

        errors = collector.get_error_breakdown()
        assert errors["total_errors"] == 3

    def test_cache_tracking(self, collector):
        """Test cache hit tracking"""
        collector.record_query("test", 0.9, 5, True, cached=True)
        collector.record_query("test", 0.9, 50, True, cached=False)

        summary = collector.get_summary()
        assert summary["cached_responses"] == 1
        assert summary["cache_hit_rate"] == 50.0

    def test_reset(self, collector):
        """Test resetting analytics"""
        collector.record_query("test", 0.9, 10, True)
        collector.reset()

        summary = collector.get_summary()
        assert summary["total_queries"] == 0


class TestWebhooks:
    """Tests for webhook manager"""

    @pytest.fixture
    def manager(self):
        from webhooks import WebhookManager, WebhookEvent
        return WebhookManager(max_retries=1, timeout=5.0)

    def test_subscribe(self, manager):
        """Test creating a subscription"""
        from webhooks import WebhookEvent

        sub = manager.subscribe(
            url="https://example.com/webhook",
            events=[WebhookEvent.QUERY_COMPLETED],
            secret="test_secret"
        )

        assert sub.id is not None
        assert sub.url == "https://example.com/webhook"
        assert sub.enabled == True

    def test_unsubscribe(self, manager):
        """Test removing a subscription"""
        from webhooks import WebhookEvent

        sub = manager.subscribe(
            url="https://example.com/webhook",
            events=[WebhookEvent.QUERY_COMPLETED]
        )

        result = manager.unsubscribe(sub.id)
        assert result == True

        # Should return None now
        assert manager.get_subscription(sub.id) is None

    def test_list_subscriptions(self, manager):
        """Test listing subscriptions"""
        from webhooks import WebhookEvent

        manager.subscribe(
            url="https://example1.com/webhook",
            events=[WebhookEvent.QUERY_COMPLETED]
        )
        manager.subscribe(
            url="https://example2.com/webhook",
            events=[WebhookEvent.QUERY_FAILED]
        )

        subs = manager.list_subscriptions()
        assert len(subs) == 2

    def test_get_subscription(self, manager):
        """Test getting a specific subscription"""
        from webhooks import WebhookEvent

        sub = manager.subscribe(
            url="https://example.com/webhook",
            events=[WebhookEvent.SYSTEM_ALERT]
        )

        retrieved = manager.get_subscription(sub.id)
        assert retrieved is not None
        assert retrieved.url == sub.url

    def test_sign_payload(self, manager):
        """Test HMAC signature generation"""
        signature = manager._sign_payload('{"test": "data"}', "secret_key")
        assert signature is not None
        assert len(signature) == 64  # SHA256 hex

    @pytest.mark.asyncio
    async def test_emit_no_subscribers(self, manager):
        """Test emitting with no subscribers"""
        from webhooks import WebhookEvent

        # Should not raise
        await manager.emit(
            WebhookEvent.QUERY_COMPLETED,
            {"intent": "test", "duration_ms": 50}
        )

    def test_subscription_metadata(self, manager):
        """Test subscription with metadata"""
        from webhooks import WebhookEvent

        sub = manager.subscribe(
            url="https://example.com/webhook",
            events=[WebhookEvent.QUERY_COMPLETED],
            metadata={"env": "production", "team": "backend"}
        )

        assert sub.metadata["env"] == "production"
        assert sub.metadata["team"] == "backend"


class TestWebhookEvents:
    """Tests for webhook event types"""

    def test_event_values(self):
        """Test event enum values"""
        from webhooks import WebhookEvent

        assert WebhookEvent.QUERY_COMPLETED.value == "query.completed"
        assert WebhookEvent.QUERY_FAILED.value == "query.failed"
        assert WebhookEvent.HEALTH_DEGRADED.value == "health.degraded"

    def test_all_events_have_values(self):
        """Test all events have string values"""
        from webhooks import WebhookEvent

        for event in WebhookEvent:
            assert isinstance(event.value, str)
            assert "." in event.value


class TestWebhookPayload:
    """Tests for webhook payload"""

    def test_payload_to_dict(self):
        """Test payload serialization"""
        from webhooks import WebhookPayload, WebhookEvent
        from datetime import datetime, timezone

        payload = WebhookPayload(
            event=WebhookEvent.QUERY_COMPLETED,
            timestamp=datetime.now(timezone.utc),
            data={"intent": "test"},
            request_id="req_123"
        )

        result = payload.to_dict()
        assert result["event"] == "query.completed"
        assert "timestamp" in result
        assert result["data"]["intent"] == "test"
        assert result["request_id"] == "req_123"


# Run tests with: pytest tests/test_analytics_webhooks.py -v
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
