"""
M537 Voice Gateway - Webhooks
Event notification system for external integrations
"""
import asyncio
import hashlib
import hmac
import json
import logging
import time
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
import threading
import httpx

logger = logging.getLogger(__name__)


class WebhookEvent(Enum):
    """Supported webhook event types"""
    QUERY_COMPLETED = "query.completed"
    QUERY_FAILED = "query.failed"
    HEALTH_DEGRADED = "health.degraded"
    HEALTH_RECOVERED = "health.recovered"
    RATE_LIMIT_EXCEEDED = "rate_limit.exceeded"
    ERROR_THRESHOLD = "error.threshold"
    SYSTEM_ALERT = "system.alert"


@dataclass
class WebhookSubscription:
    """Webhook subscription configuration"""
    id: str
    url: str
    events: List[WebhookEvent]
    secret: Optional[str] = None
    enabled: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = field(default_factory=dict)

    # Delivery tracking
    total_deliveries: int = 0
    successful_deliveries: int = 0
    failed_deliveries: int = 0
    last_delivery_at: Optional[datetime] = None
    last_error: Optional[str] = None


@dataclass
class WebhookPayload:
    """Webhook event payload"""
    event: WebhookEvent
    timestamp: datetime
    data: Dict[str, Any]
    request_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event": self.event.value,
            "timestamp": self.timestamp.isoformat(),
            "data": self.data,
            "request_id": self.request_id
        }


class WebhookManager:
    """
    Manages webhook subscriptions and delivery.

    Features:
    - Event subscription management
    - Async delivery with retries
    - HMAC signature verification
    - Delivery tracking
    """

    def __init__(
        self,
        max_retries: int = 3,
        retry_delay: float = 5.0,
        timeout: float = 10.0
    ):
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.timeout = timeout
        self._subscriptions: Dict[str, WebhookSubscription] = {}
        self._lock = threading.Lock()
        self._delivery_queue: asyncio.Queue = None
        self._worker_task: Optional[asyncio.Task] = None

    def subscribe(
        self,
        url: str,
        events: List[WebhookEvent],
        secret: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> WebhookSubscription:
        """Create a new webhook subscription"""
        import secrets as sec

        sub_id = sec.token_hex(8)
        subscription = WebhookSubscription(
            id=sub_id,
            url=url,
            events=events,
            secret=secret,
            metadata=metadata or {}
        )

        with self._lock:
            self._subscriptions[sub_id] = subscription

        logger.info(f"Created webhook subscription {sub_id} for {url}")
        return subscription

    def unsubscribe(self, subscription_id: str) -> bool:
        """Remove a webhook subscription"""
        with self._lock:
            if subscription_id in self._subscriptions:
                del self._subscriptions[subscription_id]
                logger.info(f"Removed webhook subscription {subscription_id}")
                return True
        return False

    def get_subscription(self, subscription_id: str) -> Optional[WebhookSubscription]:
        """Get a subscription by ID"""
        return self._subscriptions.get(subscription_id)

    def list_subscriptions(self) -> List[Dict[str, Any]]:
        """List all subscriptions"""
        with self._lock:
            return [
                {
                    "id": sub.id,
                    "url": sub.url,
                    "events": [e.value for e in sub.events],
                    "enabled": sub.enabled,
                    "created_at": sub.created_at.isoformat(),
                    "total_deliveries": sub.total_deliveries,
                    "successful_deliveries": sub.successful_deliveries,
                    "failed_deliveries": sub.failed_deliveries
                }
                for sub in self._subscriptions.values()
            ]

    def _sign_payload(self, payload: str, secret: str) -> str:
        """Generate HMAC signature for payload"""
        return hmac.new(
            secret.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()

    async def _deliver(
        self,
        subscription: WebhookSubscription,
        payload: WebhookPayload
    ) -> bool:
        """Deliver webhook to a single subscription"""
        payload_json = json.dumps(payload.to_dict())

        headers = {
            "Content-Type": "application/json",
            "X-Webhook-Event": payload.event.value,
            "X-Webhook-Timestamp": str(int(time.time())),
            "User-Agent": "M537-Voice-Gateway/1.0"
        }

        # Add signature if secret is configured
        if subscription.secret:
            signature = self._sign_payload(payload_json, subscription.secret)
            headers["X-Webhook-Signature"] = f"sha256={signature}"

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            for attempt in range(self.max_retries + 1):
                try:
                    response = await client.post(
                        subscription.url,
                        content=payload_json,
                        headers=headers
                    )

                    if response.status_code >= 200 and response.status_code < 300:
                        subscription.total_deliveries += 1
                        subscription.successful_deliveries += 1
                        subscription.last_delivery_at = datetime.now(timezone.utc)
                        subscription.last_error = None
                        logger.debug(
                            f"Webhook delivered to {subscription.url}: "
                            f"{payload.event.value}"
                        )
                        return True
                    else:
                        subscription.last_error = f"HTTP {response.status_code}"

                except Exception as e:
                    subscription.last_error = str(e)

                # Retry with delay
                if attempt < self.max_retries:
                    await asyncio.sleep(self.retry_delay * (attempt + 1))

        subscription.total_deliveries += 1
        subscription.failed_deliveries += 1
        logger.warning(
            f"Webhook delivery failed to {subscription.url}: "
            f"{subscription.last_error}"
        )
        return False

    async def emit(
        self,
        event: WebhookEvent,
        data: Dict[str, Any],
        request_id: Optional[str] = None
    ):
        """Emit an event to all subscribed webhooks"""
        payload = WebhookPayload(
            event=event,
            timestamp=datetime.now(timezone.utc),
            data=data,
            request_id=request_id
        )

        # Find subscriptions for this event
        with self._lock:
            subscribers = [
                sub for sub in self._subscriptions.values()
                if sub.enabled and event in sub.events
            ]

        if not subscribers:
            return

        # Deliver to all subscribers concurrently
        tasks = [
            self._deliver(sub, payload)
            for sub in subscribers
        ]
        await asyncio.gather(*tasks, return_exceptions=True)

    def emit_sync(
        self,
        event: WebhookEvent,
        data: Dict[str, Any],
        request_id: Optional[str] = None
    ):
        """Emit an event synchronously (for use in sync code)"""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                asyncio.create_task(self.emit(event, data, request_id))
            else:
                loop.run_until_complete(self.emit(event, data, request_id))
        except RuntimeError:
            # No event loop, create one
            asyncio.run(self.emit(event, data, request_id))


# Global webhook manager
webhook_manager = WebhookManager()


# Convenience functions
def emit_query_completed(intent: str, duration_ms: float, **kwargs):
    """Emit query completed event"""
    webhook_manager.emit_sync(
        WebhookEvent.QUERY_COMPLETED,
        {"intent": intent, "duration_ms": duration_ms, **kwargs}
    )


def emit_query_failed(intent: str, error_code: str, message: str, **kwargs):
    """Emit query failed event"""
    webhook_manager.emit_sync(
        WebhookEvent.QUERY_FAILED,
        {"intent": intent, "error_code": error_code, "message": message, **kwargs}
    )


def emit_health_alert(status: str, details: Dict[str, Any]):
    """Emit health alert event"""
    event = (
        WebhookEvent.HEALTH_DEGRADED
        if status in ("degraded", "unhealthy")
        else WebhookEvent.HEALTH_RECOVERED
    )
    webhook_manager.emit_sync(event, {"status": status, "details": details})


def emit_system_alert(alert_type: str, message: str, severity: str = "warning"):
    """Emit system alert event"""
    webhook_manager.emit_sync(
        WebhookEvent.SYSTEM_ALERT,
        {"type": alert_type, "message": message, "severity": severity}
    )
