"""
M537 Voice Gateway - Circuit Breaker Pattern
Resilient service calls with automatic failure detection and recovery
"""
import asyncio
import logging
import time
from datetime import datetime, timezone
from enum import Enum
from typing import Callable, Any, Optional, Dict
from dataclasses import dataclass, field
from functools import wraps
import threading

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing if service recovered


@dataclass
class CircuitStats:
    """Statistics for a circuit breaker"""
    total_calls: int = 0
    successful_calls: int = 0
    failed_calls: int = 0
    rejected_calls: int = 0
    last_failure_time: Optional[datetime] = None
    last_success_time: Optional[datetime] = None
    state_changes: int = 0


@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker"""
    failure_threshold: int = 5          # Failures before opening
    success_threshold: int = 3          # Successes to close from half-open
    timeout: float = 30.0               # Seconds before trying half-open
    half_open_max_calls: int = 3        # Max calls in half-open state
    excluded_exceptions: tuple = ()      # Exceptions that don't count as failures


class CircuitBreaker:
    """
    Circuit Breaker implementation.

    Usage:
        breaker = CircuitBreaker("external_api")

        @breaker
        async def call_external_api():
            ...

        # Or manually:
        async with breaker:
            await call_external_api()
    """

    def __init__(
        self,
        name: str,
        config: Optional[CircuitBreakerConfig] = None
    ):
        self.name = name
        self.config = config or CircuitBreakerConfig()
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._last_failure_time: Optional[float] = None
        self._half_open_calls = 0
        self._lock = threading.Lock()
        self.stats = CircuitStats()

    @property
    def state(self) -> CircuitState:
        """Get current state, checking for timeout transition"""
        if self._state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self._transition_to(CircuitState.HALF_OPEN)
        return self._state

    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to try half-open"""
        if self._last_failure_time is None:
            return True
        return time.time() - self._last_failure_time >= self.config.timeout

    def _transition_to(self, state: CircuitState):
        """Transition to a new state"""
        old_state = self._state
        self._state = state
        self.stats.state_changes += 1

        if state == CircuitState.HALF_OPEN:
            self._half_open_calls = 0

        logger.info(f"Circuit '{self.name}' transitioned: {old_state.value} -> {state.value}")

    def _record_success(self):
        """Record a successful call"""
        with self._lock:
            self.stats.total_calls += 1
            self.stats.successful_calls += 1
            self.stats.last_success_time = datetime.now(timezone.utc)

            if self._state == CircuitState.HALF_OPEN:
                self._success_count += 1
                if self._success_count >= self.config.success_threshold:
                    self._transition_to(CircuitState.CLOSED)
                    self._failure_count = 0
                    self._success_count = 0

    def _record_failure(self, exception: Exception):
        """Record a failed call"""
        # Check if exception should be excluded
        if isinstance(exception, self.config.excluded_exceptions):
            return

        with self._lock:
            self.stats.total_calls += 1
            self.stats.failed_calls += 1
            self.stats.last_failure_time = datetime.now(timezone.utc)
            self._last_failure_time = time.time()

            if self._state == CircuitState.HALF_OPEN:
                self._transition_to(CircuitState.OPEN)
                self._success_count = 0
            elif self._state == CircuitState.CLOSED:
                self._failure_count += 1
                if self._failure_count >= self.config.failure_threshold:
                    self._transition_to(CircuitState.OPEN)

    def _can_execute(self) -> bool:
        """Check if a call can be executed"""
        state = self.state

        if state == CircuitState.CLOSED:
            return True

        if state == CircuitState.OPEN:
            self.stats.rejected_calls += 1
            return False

        if state == CircuitState.HALF_OPEN:
            with self._lock:
                if self._half_open_calls < self.config.half_open_max_calls:
                    self._half_open_calls += 1
                    return True
                return False

        return False

    async def __aenter__(self):
        """Async context manager entry"""
        if not self._can_execute():
            raise CircuitOpenError(f"Circuit '{self.name}' is open")
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if exc_val is None:
            self._record_success()
        else:
            self._record_failure(exc_val)
        return False

    def __enter__(self):
        """Sync context manager entry"""
        if not self._can_execute():
            raise CircuitOpenError(f"Circuit '{self.name}' is open")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Sync context manager exit"""
        if exc_val is None:
            self._record_success()
        else:
            self._record_failure(exc_val)
        return False

    def __call__(self, func: Callable) -> Callable:
        """Decorator for wrapping functions"""
        if asyncio.iscoroutinefunction(func):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                async with self:
                    return await func(*args, **kwargs)
            return async_wrapper
        else:
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                with self:
                    return func(*args, **kwargs)
            return sync_wrapper

    def get_stats(self) -> Dict[str, Any]:
        """Get circuit breaker statistics"""
        return {
            "name": self.name,
            "state": self.state.value,
            "failure_count": self._failure_count,
            "success_count": self._success_count,
            "stats": {
                "total_calls": self.stats.total_calls,
                "successful_calls": self.stats.successful_calls,
                "failed_calls": self.stats.failed_calls,
                "rejected_calls": self.stats.rejected_calls,
                "state_changes": self.stats.state_changes,
                "last_failure": self.stats.last_failure_time.isoformat() if self.stats.last_failure_time else None,
                "last_success": self.stats.last_success_time.isoformat() if self.stats.last_success_time else None
            }
        }

    def reset(self):
        """Manually reset the circuit breaker"""
        with self._lock:
            self._state = CircuitState.CLOSED
            self._failure_count = 0
            self._success_count = 0
            self._last_failure_time = None
            self._half_open_calls = 0
            logger.info(f"Circuit '{self.name}' manually reset")


class CircuitOpenError(Exception):
    """Raised when circuit is open and call is rejected"""
    pass


class CircuitBreakerRegistry:
    """Registry for managing multiple circuit breakers"""

    def __init__(self):
        self._breakers: Dict[str, CircuitBreaker] = {}
        self._lock = threading.Lock()

    def get_or_create(
        self,
        name: str,
        config: Optional[CircuitBreakerConfig] = None
    ) -> CircuitBreaker:
        """Get existing or create new circuit breaker"""
        with self._lock:
            if name not in self._breakers:
                self._breakers[name] = CircuitBreaker(name, config)
            return self._breakers[name]

    def get(self, name: str) -> Optional[CircuitBreaker]:
        """Get a circuit breaker by name"""
        return self._breakers.get(name)

    def get_all_stats(self) -> Dict[str, Any]:
        """Get statistics for all circuit breakers"""
        return {
            name: breaker.get_stats()
            for name, breaker in self._breakers.items()
        }

    def reset_all(self):
        """Reset all circuit breakers"""
        for breaker in self._breakers.values():
            breaker.reset()


# Global registry
circuit_registry = CircuitBreakerRegistry()


def circuit_breaker(
    name: str,
    failure_threshold: int = 5,
    timeout: float = 30.0
) -> Callable:
    """
    Decorator to wrap a function with a circuit breaker.

    Usage:
        @circuit_breaker("external_api")
        async def call_external_api():
            ...
    """
    config = CircuitBreakerConfig(
        failure_threshold=failure_threshold,
        timeout=timeout
    )
    breaker = circuit_registry.get_or_create(name, config)
    return breaker
