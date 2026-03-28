"""
M537 Voice Gateway - API Authentication
API Key authentication with rate limiting per key
"""
import os
import hashlib
import secrets
import logging
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any, Tuple
from dataclasses import dataclass, field
from collections import defaultdict
import threading

from fastapi import Request, HTTPException, Security
from fastapi.security import APIKeyHeader, APIKeyQuery

logger = logging.getLogger(__name__)

# Configuration
AUTH_ENABLED = os.environ.get("AUTH_ENABLED", "false").lower() == "true"
MASTER_API_KEY = os.environ.get("MASTER_API_KEY", "")


@dataclass
class APIKeyInfo:
    """API Key metadata"""
    key_id: str
    key_hash: str
    name: str
    tier: str  # 'free', 'standard', 'premium', 'enterprise'
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: Optional[datetime] = None
    rate_limit: int = 60  # requests per minute
    enabled: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)

    def is_valid(self) -> bool:
        if not self.enabled:
            return False
        if self.expires_at and datetime.now(timezone.utc) > self.expires_at:
            return False
        return True


# Rate limit tiers (requests per minute)
RATE_LIMIT_TIERS = {
    "free": 30,
    "standard": 60,
    "premium": 300,
    "enterprise": 1000,
    "unlimited": 999999
}


class APIKeyManager:
    """
    Manages API keys with in-memory storage.
    In production, use a database or Redis.
    """

    def __init__(self):
        self.keys: Dict[str, APIKeyInfo] = {}
        self.key_usage: Dict[str, list] = defaultdict(list)
        self._lock = threading.Lock()

        # Add master key if configured
        if MASTER_API_KEY:
            self._add_master_key()

    def _add_master_key(self):
        """Add master API key from environment"""
        key_hash = self._hash_key(MASTER_API_KEY)
        self.keys[key_hash] = APIKeyInfo(
            key_id="master",
            key_hash=key_hash,
            name="Master Key",
            tier="unlimited",
            rate_limit=RATE_LIMIT_TIERS["unlimited"]
        )
        logger.info("Master API key configured")

    def _hash_key(self, key: str) -> str:
        """Hash API key for storage"""
        return hashlib.sha256(key.encode()).hexdigest()

    def generate_key(
        self,
        name: str,
        tier: str = "standard",
        expires_days: Optional[int] = None,
        metadata: Optional[Dict] = None
    ) -> Tuple[str, APIKeyInfo]:
        """Generate a new API key"""
        # Generate random key
        raw_key = f"m537_{secrets.token_urlsafe(32)}"
        key_hash = self._hash_key(raw_key)
        key_id = secrets.token_hex(8)

        expires_at = None
        if expires_days:
            expires_at = datetime.now(timezone.utc) + timedelta(days=expires_days)

        key_info = APIKeyInfo(
            key_id=key_id,
            key_hash=key_hash,
            name=name,
            tier=tier,
            expires_at=expires_at,
            rate_limit=RATE_LIMIT_TIERS.get(tier, 60),
            metadata=metadata or {}
        )

        with self._lock:
            self.keys[key_hash] = key_info

        logger.info(f"Generated API key: {key_id} ({name}, tier={tier})")
        return raw_key, key_info

    def validate_key(self, key: str) -> Optional[APIKeyInfo]:
        """Validate an API key"""
        key_hash = self._hash_key(key)

        with self._lock:
            key_info = self.keys.get(key_hash)

        if not key_info:
            return None

        if not key_info.is_valid():
            return None

        return key_info

    def check_rate_limit(self, key: str) -> Tuple[bool, int, int]:
        """
        Check if request is within rate limit.
        Returns: (allowed, remaining, reset_seconds)
        """
        key_hash = self._hash_key(key)
        now = datetime.now(timezone.utc)
        window_start = now - timedelta(minutes=1)

        with self._lock:
            key_info = self.keys.get(key_hash)
            if not key_info:
                return False, 0, 60

            # Clean old entries
            self.key_usage[key_hash] = [
                ts for ts in self.key_usage[key_hash]
                if ts > window_start
            ]

            # Check limit
            current_usage = len(self.key_usage[key_hash])
            if current_usage >= key_info.rate_limit:
                # Calculate reset time
                oldest = min(self.key_usage[key_hash]) if self.key_usage[key_hash] else now
                reset_seconds = int((oldest + timedelta(minutes=1) - now).total_seconds())
                return False, 0, max(reset_seconds, 1)

            # Record usage
            self.key_usage[key_hash].append(now)
            remaining = key_info.rate_limit - current_usage - 1

            return True, remaining, 60

    def revoke_key(self, key_id: str) -> bool:
        """Revoke an API key by ID"""
        with self._lock:
            for key_hash, info in self.keys.items():
                if info.key_id == key_id:
                    info.enabled = False
                    logger.info(f"Revoked API key: {key_id}")
                    return True
        return False

    def list_keys(self) -> list:
        """List all API keys (without sensitive data)"""
        with self._lock:
            return [
                {
                    "key_id": info.key_id,
                    "name": info.name,
                    "tier": info.tier,
                    "created_at": info.created_at.isoformat(),
                    "expires_at": info.expires_at.isoformat() if info.expires_at else None,
                    "enabled": info.enabled
                }
                for info in self.keys.values()
            ]

    def get_usage_stats(self, key_id: str) -> Optional[Dict]:
        """Get usage statistics for a key"""
        with self._lock:
            for key_hash, info in self.keys.items():
                if info.key_id == key_id:
                    now = datetime.now(timezone.utc)
                    window_start = now - timedelta(minutes=1)
                    recent_usage = [
                        ts for ts in self.key_usage[key_hash]
                        if ts > window_start
                    ]
                    return {
                        "key_id": key_id,
                        "requests_last_minute": len(recent_usage),
                        "rate_limit": info.rate_limit,
                        "tier": info.tier
                    }
        return None


# Global key manager
api_key_manager = APIKeyManager()

# FastAPI security schemes
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)
api_key_query = APIKeyQuery(name="api_key", auto_error=False)


async def get_api_key(
    request: Request,
    api_key_header_value: str = Security(api_key_header),
    api_key_query_value: str = Security(api_key_query)
) -> Optional[APIKeyInfo]:
    """
    Dependency to validate API key from header or query param.
    Returns None if auth is disabled.
    """
    if not AUTH_ENABLED:
        return None

    # Get key from header or query
    api_key = api_key_header_value or api_key_query_value

    if not api_key:
        raise HTTPException(
            status_code=401,
            detail={
                "error": {
                    "code": "MISSING_API_KEY",
                    "message": "API key required. Provide via X-API-Key header or api_key query parameter."
                }
            }
        )

    # Validate key
    key_info = api_key_manager.validate_key(api_key)
    if not key_info:
        raise HTTPException(
            status_code=401,
            detail={
                "error": {
                    "code": "INVALID_API_KEY",
                    "message": "Invalid or expired API key."
                }
            }
        )

    # Check rate limit
    allowed, remaining, reset = api_key_manager.check_rate_limit(api_key)
    if not allowed:
        raise HTTPException(
            status_code=429,
            detail={
                "error": {
                    "code": "RATE_LIMIT_EXCEEDED",
                    "message": f"Rate limit exceeded. Try again in {reset} seconds."
                }
            },
            headers={
                "X-RateLimit-Limit": str(key_info.rate_limit),
                "X-RateLimit-Remaining": "0",
                "Retry-After": str(reset)
            }
        )

    # Add rate limit headers to response
    request.state.rate_limit_remaining = remaining
    request.state.rate_limit_limit = key_info.rate_limit

    return key_info


class AuthMiddleware:
    """Middleware to add rate limit headers to all responses"""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                headers = list(message.get("headers", []))

                # Add rate limit headers if available
                if hasattr(scope.get("state", {}), "rate_limit_remaining"):
                    state = scope["state"]
                    headers.extend([
                        (b"x-ratelimit-limit", str(state.rate_limit_limit).encode()),
                        (b"x-ratelimit-remaining", str(state.rate_limit_remaining).encode()),
                    ])

                message = {**message, "headers": headers}

            await send(message)

        await self.app(scope, receive, send_wrapper)
