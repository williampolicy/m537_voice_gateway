"""
M537 Voice Gateway - Rate Limiter Tests
"""
import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))


class TestRateLimitState:
    """Rate limit state tests"""

    def test_initial_request_allowed(self):
        """First request should always be allowed"""
        from middleware.rate_limiter import RateLimitState
        from unittest.mock import MagicMock

        state = RateLimitState(requests_per_minute=60, burst_size=10)

        # Create mock request
        request = MagicMock()
        request.headers = {}
        request.client.host = "192.168.1.1"

        allowed, remaining, retry_after = state.check_rate_limit(request)
        assert allowed == True
        assert remaining == 9  # burst_size - 1
        assert retry_after == 0

    def test_burst_requests_allowed(self):
        """Burst requests within limit should be allowed"""
        from middleware.rate_limiter import RateLimitState
        from unittest.mock import MagicMock

        state = RateLimitState(requests_per_minute=60, burst_size=5)

        request = MagicMock()
        request.headers = {}
        request.client.host = "192.168.1.2"

        # Make burst requests
        for i in range(5):
            allowed, remaining, retry_after = state.check_rate_limit(request)
            assert allowed == True
            assert remaining == 5 - i - 1

    def test_exceed_burst_blocked(self):
        """Requests exceeding burst should be blocked"""
        from middleware.rate_limiter import RateLimitState
        from unittest.mock import MagicMock

        state = RateLimitState(requests_per_minute=60, burst_size=3)

        request = MagicMock()
        request.headers = {}
        request.client.host = "192.168.1.3"

        # Use up burst
        for _ in range(3):
            state.check_rate_limit(request)

        # This should be blocked
        allowed, remaining, retry_after = state.check_rate_limit(request)
        assert allowed == False
        assert remaining == 0
        assert retry_after > 0

    def test_different_ips_independent(self):
        """Different IPs should have independent limits"""
        from middleware.rate_limiter import RateLimitState
        from unittest.mock import MagicMock

        state = RateLimitState(requests_per_minute=60, burst_size=2)

        request1 = MagicMock()
        request1.headers = {}
        request1.client.host = "192.168.1.10"

        request2 = MagicMock()
        request2.headers = {}
        request2.client.host = "192.168.1.11"

        # Use up IP1's burst
        for _ in range(2):
            state.check_rate_limit(request1)

        # IP2 should still be allowed
        allowed, _, _ = state.check_rate_limit(request2)
        assert allowed == True

    def test_x_forwarded_for_header(self):
        """Should extract IP from X-Forwarded-For header"""
        from middleware.rate_limiter import RateLimitState
        from unittest.mock import MagicMock

        state = RateLimitState(requests_per_minute=60, burst_size=10)

        request = MagicMock()
        request.headers = {"X-Forwarded-For": "10.0.0.1, 192.168.1.1"}
        request.client.host = "127.0.0.1"

        state.check_rate_limit(request)

        # Verify the forwarded IP is used
        assert "10.0.0.1" in state._buckets

    def test_metrics(self):
        """Should track metrics correctly"""
        from middleware.rate_limiter import RateLimitState
        from unittest.mock import MagicMock

        state = RateLimitState(requests_per_minute=60, burst_size=2)

        request = MagicMock()
        request.headers = {}
        request.client.host = "192.168.1.20"

        # Make 3 requests (2 allowed, 1 blocked)
        for _ in range(3):
            state.check_rate_limit(request)

        metrics = state.get_metrics()
        assert metrics["total_requests"] == 3
        assert metrics["blocked_requests"] == 1
        assert metrics["active_clients"] == 1

    def test_cleanup_old_entries(self):
        """Should clean up old entries"""
        from middleware.rate_limiter import RateLimitState
        from unittest.mock import MagicMock
        import time

        state = RateLimitState(requests_per_minute=60, burst_size=10)

        request = MagicMock()
        request.headers = {}
        request.client.host = "192.168.1.30"

        state.check_rate_limit(request)
        assert len(state._buckets) == 1

        # Manually set old timestamp
        state._buckets["192.168.1.30"] = (10, time.time() - 600)

        state.cleanup_old_entries(max_age_seconds=300)
        assert len(state._buckets) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
