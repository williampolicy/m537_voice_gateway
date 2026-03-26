"""
M537 Voice Gateway - Test Configuration
"""
import pytest
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))


@pytest.fixture(autouse=True)
def reset_rate_limiter():
    """Reset rate limiter state before each test"""
    from middleware.rate_limiter import rate_limit_state

    # Clear rate limit buckets before each test
    rate_limit_state._buckets.clear()
    rate_limit_state.total_requests = 0
    rate_limit_state.blocked_requests = 0

    yield

    # Clean up after test
    rate_limit_state._buckets.clear()
