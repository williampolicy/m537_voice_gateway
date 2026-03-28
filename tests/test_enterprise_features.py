"""
M537 Voice Gateway - Enterprise Features Tests
Tests for authentication, circuit breaker, and graceful shutdown
"""
import pytest
import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))


class TestAPIAuthentication:
    """Tests for API key authentication"""

    @pytest.fixture
    def key_manager(self):
        from auth import APIKeyManager
        return APIKeyManager()

    def test_generate_key(self, key_manager):
        """Test generating a new API key"""
        raw_key, info = key_manager.generate_key("Test Key", tier="standard")

        assert raw_key.startswith("m537_")
        assert info.name == "Test Key"
        assert info.tier == "standard"
        assert info.enabled == True

    def test_validate_key(self, key_manager):
        """Test validating an API key"""
        raw_key, _ = key_manager.generate_key("Validate Test")

        info = key_manager.validate_key(raw_key)
        assert info is not None
        assert info.name == "Validate Test"

    def test_invalid_key(self, key_manager):
        """Test invalid key returns None"""
        info = key_manager.validate_key("invalid_key_12345")
        assert info is None

    def test_rate_limit_check(self, key_manager):
        """Test rate limit checking"""
        raw_key, info = key_manager.generate_key("Rate Test", tier="free")

        # First call should be allowed
        allowed, remaining, reset = key_manager.check_rate_limit(raw_key)
        assert allowed == True
        assert remaining < info.rate_limit

    def test_rate_limit_exceeded(self, key_manager):
        """Test rate limit exceeded"""
        raw_key, _ = key_manager.generate_key("Limit Test", tier="free")

        # Exhaust rate limit
        for _ in range(35):  # Free tier is 30/min
            key_manager.check_rate_limit(raw_key)

        allowed, remaining, reset = key_manager.check_rate_limit(raw_key)
        assert allowed == False
        assert remaining == 0

    def test_revoke_key(self, key_manager):
        """Test revoking an API key"""
        raw_key, info = key_manager.generate_key("Revoke Test")
        key_id = info.key_id

        result = key_manager.revoke_key(key_id)
        assert result == True

        # Key should no longer validate
        info = key_manager.validate_key(raw_key)
        assert info is None

    def test_list_keys(self, key_manager):
        """Test listing all keys"""
        key_manager.generate_key("Key 1")
        key_manager.generate_key("Key 2")

        keys = key_manager.list_keys()
        assert len(keys) >= 2

    def test_tier_rate_limits(self, key_manager):
        """Test different tier rate limits"""
        from auth import RATE_LIMIT_TIERS

        _, free_info = key_manager.generate_key("Free", tier="free")
        _, premium_info = key_manager.generate_key("Premium", tier="premium")

        assert free_info.rate_limit == RATE_LIMIT_TIERS["free"]
        assert premium_info.rate_limit == RATE_LIMIT_TIERS["premium"]
        assert premium_info.rate_limit > free_info.rate_limit


class TestCircuitBreaker:
    """Tests for circuit breaker pattern"""

    @pytest.fixture
    def breaker(self):
        from circuit_breaker import CircuitBreaker, CircuitBreakerConfig
        config = CircuitBreakerConfig(
            failure_threshold=3,
            success_threshold=2,
            timeout=1.0
        )
        return CircuitBreaker("test_breaker", config)

    def test_initial_state_closed(self, breaker):
        """Test initial state is closed"""
        from circuit_breaker import CircuitState
        assert breaker.state == CircuitState.CLOSED

    def test_opens_after_failures(self, breaker):
        """Test circuit opens after threshold failures"""
        from circuit_breaker import CircuitState

        for _ in range(3):
            try:
                with breaker:
                    raise ValueError("Test error")
            except ValueError:
                pass

        assert breaker.state == CircuitState.OPEN

    def test_rejects_when_open(self, breaker):
        """Test circuit rejects calls when open"""
        from circuit_breaker import CircuitOpenError

        # Open the circuit
        for _ in range(3):
            try:
                with breaker:
                    raise ValueError("Test error")
            except ValueError:
                pass

        # Should reject
        with pytest.raises(CircuitOpenError):
            with breaker:
                pass

    def test_half_open_after_timeout(self, breaker):
        """Test circuit goes half-open after timeout"""
        from circuit_breaker import CircuitState
        import time

        # Open the circuit
        for _ in range(3):
            try:
                with breaker:
                    raise ValueError("Test error")
            except ValueError:
                pass

        # Wait for timeout
        time.sleep(1.1)

        # Should be half-open now
        assert breaker.state == CircuitState.HALF_OPEN

    def test_closes_after_successes(self, breaker):
        """Test circuit closes after successful calls"""
        from circuit_breaker import CircuitState
        import time

        # Open the circuit
        for _ in range(3):
            try:
                with breaker:
                    raise ValueError("Test error")
            except ValueError:
                pass

        # Wait for timeout
        time.sleep(1.1)

        # Successful calls
        for _ in range(2):
            with breaker:
                pass

        assert breaker.state == CircuitState.CLOSED

    def test_decorator_usage(self):
        """Test circuit breaker as decorator"""
        from circuit_breaker import circuit_breaker

        call_count = 0

        @circuit_breaker("decorator_test")
        def test_func():
            nonlocal call_count
            call_count += 1
            return "success"

        result = test_func()
        assert result == "success"
        assert call_count == 1

    def test_stats(self, breaker):
        """Test circuit breaker statistics"""
        with breaker:
            pass

        stats = breaker.get_stats()
        assert stats["name"] == "test_breaker"
        assert stats["stats"]["successful_calls"] == 1

    def test_manual_reset(self, breaker):
        """Test manual circuit reset"""
        from circuit_breaker import CircuitState

        # Open the circuit
        for _ in range(3):
            try:
                with breaker:
                    raise ValueError("Test error")
            except ValueError:
                pass

        assert breaker.state == CircuitState.OPEN

        breaker.reset()
        assert breaker.state == CircuitState.CLOSED


class TestGracefulShutdown:
    """Tests for graceful shutdown"""

    @pytest.fixture
    def shutdown_manager(self):
        from graceful_shutdown import GracefulShutdown
        return GracefulShutdown(shutdown_timeout=5.0, drain_timeout=2.0)

    @pytest.mark.asyncio
    async def test_initial_state(self, shutdown_manager):
        """Test initial state is not shutting down"""
        assert shutdown_manager.is_shutting_down == False
        assert shutdown_manager.active_request_count == 0

    @pytest.mark.asyncio
    async def test_track_request(self, shutdown_manager):
        """Test request tracking"""
        async with shutdown_manager.track_request() as req_id:
            assert shutdown_manager.active_request_count == 1
            assert req_id.startswith("req_")

        assert shutdown_manager.active_request_count == 0

    @pytest.mark.asyncio
    async def test_multiple_requests(self, shutdown_manager):
        """Test tracking multiple requests"""
        req1 = await shutdown_manager.register_request()
        req2 = await shutdown_manager.register_request()

        assert shutdown_manager.active_request_count == 2

        await shutdown_manager.unregister_request(req1)
        assert shutdown_manager.active_request_count == 1

        await shutdown_manager.unregister_request(req2)
        assert shutdown_manager.active_request_count == 0

    @pytest.mark.asyncio
    async def test_cleanup_callbacks(self, shutdown_manager):
        """Test cleanup callbacks are called"""
        cleanup_called = False

        async def cleanup():
            nonlocal cleanup_called
            cleanup_called = True

        shutdown_manager.add_cleanup_callback(cleanup, "test_cleanup")
        await shutdown_manager.shutdown()

        assert cleanup_called == True

    @pytest.mark.asyncio
    async def test_rejects_during_shutdown(self, shutdown_manager):
        """Test new requests rejected during shutdown"""
        from graceful_shutdown import ShutdownInProgressError

        # Start shutdown
        shutdown_task = asyncio.create_task(shutdown_manager.shutdown())

        # Give it a moment to set shutting_down flag
        await asyncio.sleep(0.1)

        # Try to track new request
        with pytest.raises(ShutdownInProgressError):
            async with shutdown_manager.track_request():
                pass

        await shutdown_task

    @pytest.mark.asyncio
    async def test_get_status(self, shutdown_manager):
        """Test getting shutdown status"""
        status = shutdown_manager.get_status()

        assert "is_shutting_down" in status
        assert "active_requests" in status
        assert status["is_shutting_down"] == False


class TestCircuitBreakerRegistry:
    """Tests for circuit breaker registry"""

    def test_get_or_create(self):
        """Test getting or creating circuit breakers"""
        from circuit_breaker import CircuitBreakerRegistry

        registry = CircuitBreakerRegistry()

        breaker1 = registry.get_or_create("test1")
        breaker2 = registry.get_or_create("test1")

        assert breaker1 is breaker2

    def test_get_all_stats(self):
        """Test getting all circuit breaker stats"""
        from circuit_breaker import CircuitBreakerRegistry

        registry = CircuitBreakerRegistry()
        registry.get_or_create("breaker1")
        registry.get_or_create("breaker2")

        stats = registry.get_all_stats()
        assert "breaker1" in stats
        assert "breaker2" in stats


# Run tests with: pytest tests/test_enterprise_features.py -v
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
