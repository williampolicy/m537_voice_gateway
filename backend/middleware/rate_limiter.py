"""
M537 Voice Gateway - Rate Limiting Middleware
Token bucket algorithm for request throttling
"""
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from datetime import datetime, timezone
from collections import defaultdict
import time
import threading
from typing import Dict, Tuple

from settings import settings


class RateLimitState:
    """Thread-safe rate limit state tracker using token bucket algorithm"""

    def __init__(self, requests_per_minute: int = 60, burst_size: int = 10):
        self.requests_per_minute = requests_per_minute
        self.burst_size = burst_size
        self.tokens_per_second = requests_per_minute / 60.0
        self._buckets: Dict[str, Tuple[float, float]] = {}  # ip -> (tokens, last_update)
        self._lock = threading.Lock()

        # Metrics
        self.total_requests = 0
        self.blocked_requests = 0

    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP from request"""
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"

    def check_rate_limit(self, request: Request) -> Tuple[bool, int, int]:
        """
        Check if request is allowed under rate limit.
        Returns: (allowed, remaining_tokens, retry_after_seconds)
        """
        client_ip = self._get_client_ip(request)
        current_time = time.time()

        with self._lock:
            self.total_requests += 1

            if client_ip not in self._buckets:
                # New client - full bucket
                self._buckets[client_ip] = (self.burst_size - 1, current_time)
                return True, self.burst_size - 1, 0

            tokens, last_update = self._buckets[client_ip]

            # Calculate tokens to add based on time elapsed
            time_elapsed = current_time - last_update
            tokens_to_add = time_elapsed * self.tokens_per_second
            tokens = min(self.burst_size, tokens + tokens_to_add)

            if tokens >= 1:
                # Allow request, consume one token
                self._buckets[client_ip] = (tokens - 1, current_time)
                return True, int(tokens - 1), 0
            else:
                # Rate limited
                self.blocked_requests += 1
                # Calculate retry-after
                tokens_needed = 1 - tokens
                retry_after = int(tokens_needed / self.tokens_per_second) + 1
                self._buckets[client_ip] = (tokens, current_time)
                return False, 0, retry_after

    def cleanup_old_entries(self, max_age_seconds: int = 300):
        """Remove entries older than max_age_seconds"""
        current_time = time.time()
        with self._lock:
            to_delete = [
                ip for ip, (_, last_update) in self._buckets.items()
                if current_time - last_update > max_age_seconds
            ]
            for ip in to_delete:
                del self._buckets[ip]

    def get_metrics(self) -> Dict:
        """Get rate limiting metrics"""
        with self._lock:
            return {
                "total_requests": self.total_requests,
                "blocked_requests": self.blocked_requests,
                "active_clients": len(self._buckets),
                "rate_limit_per_minute": self.requests_per_minute,
                "burst_size": self.burst_size
            }


# Global rate limit state instance
rate_limit_state = RateLimitState(
    requests_per_minute=settings.RATE_LIMIT_PER_MINUTE,
    burst_size=10
)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware"""

    # Paths exempt from rate limiting
    EXEMPT_PATHS = {"/health", "/api/health", "/api/metrics", "/docs", "/redoc", "/openapi.json"}

    async def dispatch(self, request: Request, call_next) -> Response:
        # Skip rate limiting for exempt paths and static files
        if request.url.path in self.EXEMPT_PATHS:
            return await call_next(request)

        if request.url.path.startswith(("/css/", "/js/", "/assets/")):
            return await call_next(request)

        # Check rate limit
        allowed, remaining, retry_after = rate_limit_state.check_rate_limit(request)

        if not allowed:
            return JSONResponse(
                status_code=429,
                content={
                    "success": False,
                    "error": {
                        "code": "RATE_LIMIT_EXCEEDED",
                        "message": "请求过于频繁，请稍后再试。",
                        "retry_after": retry_after
                    },
                    "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
                },
                headers={
                    "Retry-After": str(retry_after),
                    "X-RateLimit-Limit": str(rate_limit_state.requests_per_minute),
                    "X-RateLimit-Remaining": "0"
                }
            )

        # Process request and add rate limit headers
        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(rate_limit_state.requests_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(remaining)

        return response
