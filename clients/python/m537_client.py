"""
M537 Voice Gateway - Python Client
Enterprise-grade SDK with full feature support

Features:
- API Key authentication
- Voice query with caching
- Analytics endpoints
- Webhook management
- Health monitoring
- Automatic retries with exponential backoff
"""
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List, Callable
from enum import Enum
import json
import urllib.request
import urllib.error
import time
import hashlib
import hmac
import logging

logger = logging.getLogger(__name__)


class RateLimitTier(Enum):
    """API rate limit tiers"""
    FREE = "free"
    STANDARD = "standard"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"


@dataclass
class VoiceQueryRequest:
    """Voice query request"""
    transcript: str
    session_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
    language: Optional[str] = None
    include_raw: bool = False


@dataclass
class VoiceQueryData:
    """Voice query response data"""
    answer_text: str
    intent: str
    confidence: float
    tool_used: str
    suggestions: List[str]
    cached: bool
    language: str
    raw_data: Optional[Dict[str, Any]] = None


@dataclass
class ErrorInfo:
    """Error information"""
    code: str
    message: str
    suggestions: Optional[List[str]] = None


@dataclass
class VoiceQueryResponse:
    """Voice query response"""
    success: bool
    timestamp: str
    request_id: str
    api_version: str
    data: Optional[VoiceQueryData] = None
    error: Optional[ErrorInfo] = None


@dataclass
class HealthCheck:
    """Health check result"""
    name: str
    status: str
    latency_ms: float
    details: Optional[Dict[str, Any]] = None


@dataclass
class HealthResponse:
    """Health check response"""
    status: str
    version: str
    api_version: str
    timestamp: str
    uptime_seconds: int
    checks: List[HealthCheck]


@dataclass
class AnalyticsSummary:
    """Analytics summary"""
    total_queries: int
    successful_queries: int
    failed_queries: int
    cache_hit_rate: float
    avg_latency_ms: float
    p95_latency_ms: float
    p99_latency_ms: float
    top_intents: List[Dict[str, Any]]
    language_distribution: Dict[str, int]


@dataclass
class WebhookSubscription:
    """Webhook subscription"""
    id: str
    url: str
    events: List[str]
    enabled: bool
    total_deliveries: int = 0
    successful_deliveries: int = 0
    failed_deliveries: int = 0


class M537ClientError(Exception):
    """Base exception for M537 client errors"""
    pass


class AuthenticationError(M537ClientError):
    """Authentication failed"""
    pass


class RateLimitError(M537ClientError):
    """Rate limit exceeded"""
    def __init__(self, message: str, retry_after: int = 60):
        super().__init__(message)
        self.retry_after = retry_after


class M537Client:
    """
    M537 Voice Gateway API Client

    Enterprise-grade client with:
    - API Key authentication
    - Automatic retries
    - Rate limit handling
    - Full feature support

    Usage:
        client = M537Client(
            base_url="https://voice.example.com",
            api_key="your-api-key"
        )

        # Voice query
        response = client.query(VoiceQueryRequest(transcript="服务器状态"))

        # Health check
        health = client.health()

        # Analytics
        stats = client.get_analytics()
    """

    def __init__(
        self,
        base_url: str = "http://localhost:5537",
        api_key: Optional[str] = None,
        timeout: int = 30,
        max_retries: int = 3,
        retry_delay: float = 1.0
    ):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay

    # ==================== Voice API ====================

    def query(self, request: VoiceQueryRequest) -> VoiceQueryResponse:
        """
        Send a voice query.

        Args:
            request: Voice query request with transcript

        Returns:
            VoiceQueryResponse with answer and metadata

        Raises:
            AuthenticationError: If API key is invalid
            RateLimitError: If rate limit exceeded
            M537ClientError: For other errors
        """
        data = {
            "transcript": request.transcript,
            "session_id": request.session_id,
            "context": request.context or {},
            "language": request.language,
            "include_raw": request.include_raw
        }
        data = {k: v for k, v in data.items() if v is not None}

        result = self._post("/api/v1/voice-query", data)
        return self._parse_voice_response(result)

    # ==================== Health API ====================

    def health(self) -> HealthResponse:
        """Get detailed health status"""
        result = self._get("/api/v1/health")
        return self._parse_health_response(result)

    def health_summary(self) -> Dict[str, Any]:
        """Get quick health summary"""
        return self._get("/api/v1/health/summary")

    def is_healthy(self) -> bool:
        """Check if service is healthy"""
        try:
            result = self.health_summary()
            return result.get("status") == "healthy"
        except Exception:
            return False

    # ==================== Metrics API ====================

    def metrics(self) -> Dict[str, Any]:
        """Get metrics in JSON format"""
        return self._get("/api/metrics/json")

    def metrics_prometheus(self) -> str:
        """Get metrics in Prometheus format"""
        return self._get_text("/api/metrics")

    # ==================== Analytics API ====================

    def get_analytics(self) -> AnalyticsSummary:
        """Get analytics summary"""
        result = self._get("/api/analytics/summary")
        return AnalyticsSummary(
            total_queries=result.get("total_queries", 0),
            successful_queries=result.get("successful_queries", 0),
            failed_queries=result.get("failed_queries", 0),
            cache_hit_rate=result.get("cache_hit_rate", 0),
            avg_latency_ms=result.get("avg_latency_ms", 0),
            p95_latency_ms=result.get("p95_latency_ms", 0),
            p99_latency_ms=result.get("p99_latency_ms", 0),
            top_intents=result.get("top_intents", []),
            language_distribution=result.get("language_distribution", {})
        )

    def get_analytics_trend(self, hours: int = 24) -> Dict[str, Any]:
        """Get hourly analytics trend"""
        return self._get(f"/api/analytics/trend?hours={hours}")

    def get_intent_breakdown(self) -> Dict[str, Any]:
        """Get intent usage breakdown"""
        return self._get("/api/analytics/intents")

    def get_error_breakdown(self) -> Dict[str, Any]:
        """Get error breakdown"""
        return self._get("/api/analytics/errors")

    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics"""
        return self._get("/api/analytics/performance")

    # ==================== Webhook API ====================

    def list_webhooks(self) -> List[WebhookSubscription]:
        """List all webhook subscriptions"""
        result = self._get("/api/webhooks")
        webhooks = []
        for w in result.get("webhooks", []):
            webhooks.append(WebhookSubscription(
                id=w.get("id", ""),
                url=w.get("url", ""),
                events=w.get("events", []),
                enabled=w.get("enabled", False),
                total_deliveries=w.get("total_deliveries", 0),
                successful_deliveries=w.get("successful_deliveries", 0),
                failed_deliveries=w.get("failed_deliveries", 0)
            ))
        return webhooks

    def create_webhook(
        self,
        url: str,
        events: List[str],
        secret: Optional[str] = None
    ) -> WebhookSubscription:
        """
        Create a webhook subscription.

        Args:
            url: Webhook endpoint URL
            events: List of events to subscribe to
            secret: Optional HMAC secret for signature verification

        Available events:
            - query.completed
            - query.failed
            - health.degraded
            - health.recovered
            - rate_limit.exceeded
            - error.threshold
            - system.alert
        """
        data = {
            "url": url,
            "events": events,
            "secret": secret
        }
        result = self._post("/api/webhooks", data)
        w = result.get("webhook", {})
        return WebhookSubscription(
            id=w.get("id", ""),
            url=w.get("url", ""),
            events=w.get("events", []),
            enabled=w.get("enabled", False)
        )

    def get_webhook(self, webhook_id: str) -> WebhookSubscription:
        """Get webhook subscription details"""
        result = self._get(f"/api/webhooks/{webhook_id}")
        return WebhookSubscription(
            id=result.get("id", ""),
            url=result.get("url", ""),
            events=result.get("events", []),
            enabled=result.get("enabled", False),
            total_deliveries=result.get("total_deliveries", 0),
            successful_deliveries=result.get("successful_deliveries", 0),
            failed_deliveries=result.get("failed_deliveries", 0)
        )

    def delete_webhook(self, webhook_id: str) -> bool:
        """Delete a webhook subscription"""
        result = self._delete(f"/api/webhooks/{webhook_id}")
        return result.get("success", False)

    def list_webhook_events(self) -> List[Dict[str, str]]:
        """List available webhook events"""
        result = self._get("/api/webhooks/events/list")
        return result.get("events", [])

    # ==================== Internal Methods ====================

    def _get_headers(self) -> Dict[str, str]:
        """Get request headers with authentication"""
        headers = {
            "Accept": "application/json",
            "User-Agent": "M537-Python-Client/1.0"
        }
        if self.api_key:
            headers["X-API-Key"] = self.api_key
        return headers

    def _get(self, path: str) -> Dict[str, Any]:
        """Make GET request with retries"""
        return self._request("GET", path)

    def _get_text(self, path: str) -> str:
        """Make GET request and return text"""
        url = f"{self.base_url}{path}"
        req = urllib.request.Request(url)
        for key, value in self._get_headers().items():
            req.add_header(key, value)

        with urllib.request.urlopen(req, timeout=self.timeout) as response:
            return response.read().decode()

    def _post(self, path: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Make POST request with retries"""
        return self._request("POST", path, data)

    def _delete(self, path: str) -> Dict[str, Any]:
        """Make DELETE request"""
        return self._request("DELETE", path)

    def _request(
        self,
        method: str,
        path: str,
        data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make HTTP request with retries and error handling"""
        url = f"{self.base_url}{path}"
        last_error = None

        for attempt in range(self.max_retries):
            try:
                if data:
                    body = json.dumps(data).encode("utf-8")
                    req = urllib.request.Request(url, data=body, method=method)
                    req.add_header("Content-Type", "application/json")
                else:
                    req = urllib.request.Request(url, method=method)

                for key, value in self._get_headers().items():
                    req.add_header(key, value)

                with urllib.request.urlopen(req, timeout=self.timeout) as response:
                    return json.loads(response.read().decode())

            except urllib.error.HTTPError as e:
                if e.code == 401:
                    raise AuthenticationError("Invalid API key")
                elif e.code == 429:
                    retry_after = int(e.headers.get("Retry-After", 60))
                    raise RateLimitError(
                        "Rate limit exceeded",
                        retry_after=retry_after
                    )
                elif e.code >= 500:
                    last_error = e
                    if attempt < self.max_retries - 1:
                        delay = self.retry_delay * (2 ** attempt)
                        logger.warning(
                            f"Request failed with {e.code}, "
                            f"retrying in {delay}s..."
                        )
                        time.sleep(delay)
                        continue
                else:
                    try:
                        error_body = json.loads(e.read().decode())
                        return error_body
                    except:
                        raise M537ClientError(f"HTTP {e.code}: {e.reason}")

            except urllib.error.URLError as e:
                last_error = e
                if attempt < self.max_retries - 1:
                    delay = self.retry_delay * (2 ** attempt)
                    logger.warning(
                        f"Connection failed, retrying in {delay}s..."
                    )
                    time.sleep(delay)
                    continue

        raise M537ClientError(f"Request failed after {self.max_retries} attempts: {last_error}")

    def _parse_voice_response(self, data: Dict[str, Any]) -> VoiceQueryResponse:
        """Parse voice query response"""
        voice_data = None
        error = None

        if data.get("data"):
            d = data["data"]
            voice_data = VoiceQueryData(
                answer_text=d.get("answer_text", ""),
                intent=d.get("intent", ""),
                confidence=d.get("confidence", 0),
                tool_used=d.get("tool_used", ""),
                suggestions=d.get("suggestions", []),
                cached=d.get("cached", False),
                language=d.get("language", "zh-CN"),
                raw_data=d.get("raw_data")
            )

        if data.get("error"):
            e = data["error"]
            error = ErrorInfo(
                code=e.get("code", "UNKNOWN"),
                message=e.get("message", "Unknown error"),
                suggestions=e.get("suggestions")
            )

        return VoiceQueryResponse(
            success=data.get("success", False),
            timestamp=data.get("timestamp", ""),
            request_id=data.get("request_id", ""),
            api_version=data.get("api_version", "v1"),
            data=voice_data,
            error=error
        )

    def _parse_health_response(self, data: Dict[str, Any]) -> HealthResponse:
        """Parse health response"""
        checks = []
        for c in data.get("checks", []):
            checks.append(HealthCheck(
                name=c.get("name", ""),
                status=c.get("status", "unknown"),
                latency_ms=c.get("latency_ms", 0),
                details=c.get("details")
            ))

        return HealthResponse(
            status=data.get("status", "unknown"),
            version=data.get("version", ""),
            api_version=data.get("api_version", "v1"),
            timestamp=data.get("timestamp", ""),
            uptime_seconds=data.get("uptime_seconds", 0),
            checks=checks
        )


# ==================== Webhook Signature Verification ====================

def verify_webhook_signature(
    payload: bytes,
    signature: str,
    secret: str,
    timestamp: str
) -> bool:
    """
    Verify webhook signature.

    Args:
        payload: Raw request body
        signature: X-M537-Signature header value
        secret: Your webhook secret
        timestamp: X-M537-Timestamp header value

    Returns:
        True if signature is valid
    """
    message = f"{timestamp}.{payload.decode()}"
    expected = hmac.new(
        secret.encode(),
        message.encode(),
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(f"sha256={expected}", signature)


# ==================== Convenience Functions ====================

def create_client(
    base_url: str = "http://localhost:5537",
    api_key: Optional[str] = None
) -> M537Client:
    """Create a new M537 client"""
    return M537Client(base_url=base_url, api_key=api_key)


# ==================== Quick Query Function ====================

def quick_query(
    transcript: str,
    base_url: str = "http://localhost:5537",
    api_key: Optional[str] = None
) -> str:
    """
    Quick one-liner query.

    Args:
        transcript: The query text
        base_url: API base URL
        api_key: Optional API key

    Returns:
        The answer text
    """
    client = M537Client(base_url=base_url, api_key=api_key)
    response = client.query(VoiceQueryRequest(transcript=transcript))
    if response.success and response.data:
        return response.data.answer_text
    elif response.error:
        return f"Error: {response.error.message}"
    return "Unknown error"
