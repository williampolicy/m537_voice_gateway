"""
M537 Voice Gateway - Webhook Routes
API endpoints for webhook management
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, HttpUrl
from typing import List, Optional

from webhooks import webhook_manager, WebhookEvent

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


class WebhookCreateRequest(BaseModel):
    """Request to create a webhook subscription"""
    url: HttpUrl
    events: List[str]
    secret: Optional[str] = None
    metadata: Optional[dict] = None


class WebhookResponse(BaseModel):
    """Webhook subscription response"""
    id: str
    url: str
    events: List[str]
    enabled: bool


@router.get("")
async def list_webhooks():
    """
    List all webhook subscriptions.

    Returns all registered webhooks with their delivery statistics.
    """
    return {
        "webhooks": webhook_manager.list_subscriptions()
    }


@router.post("")
async def create_webhook(request: WebhookCreateRequest):
    """
    Create a new webhook subscription.

    Supported events:
    - query.completed
    - query.failed
    - health.degraded
    - health.recovered
    - rate_limit.exceeded
    - error.threshold
    - system.alert
    """
    # Validate events
    valid_events = []
    for event_name in request.events:
        try:
            event = WebhookEvent(event_name)
            valid_events.append(event)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid event: {event_name}. Valid events: {[e.value for e in WebhookEvent]}"
            )

    subscription = webhook_manager.subscribe(
        url=str(request.url),
        events=valid_events,
        secret=request.secret,
        metadata=request.metadata
    )

    return {
        "success": True,
        "webhook": {
            "id": subscription.id,
            "url": subscription.url,
            "events": [e.value for e in subscription.events],
            "enabled": subscription.enabled
        }
    }


@router.get("/{webhook_id}")
async def get_webhook(webhook_id: str):
    """
    Get webhook subscription details.
    """
    subscription = webhook_manager.get_subscription(webhook_id)
    if not subscription:
        raise HTTPException(status_code=404, detail="Webhook not found")

    return {
        "id": subscription.id,
        "url": subscription.url,
        "events": [e.value for e in subscription.events],
        "enabled": subscription.enabled,
        "created_at": subscription.created_at.isoformat(),
        "total_deliveries": subscription.total_deliveries,
        "successful_deliveries": subscription.successful_deliveries,
        "failed_deliveries": subscription.failed_deliveries,
        "last_delivery_at": subscription.last_delivery_at.isoformat() if subscription.last_delivery_at else None,
        "last_error": subscription.last_error
    }


@router.delete("/{webhook_id}")
async def delete_webhook(webhook_id: str):
    """
    Delete a webhook subscription.
    """
    if webhook_manager.unsubscribe(webhook_id):
        return {"success": True, "message": "Webhook deleted"}
    raise HTTPException(status_code=404, detail="Webhook not found")


@router.get("/events/list")
async def list_webhook_events():
    """
    List all available webhook events.
    """
    return {
        "events": [
            {
                "name": event.value,
                "description": _get_event_description(event)
            }
            for event in WebhookEvent
        ]
    }


def _get_event_description(event: WebhookEvent) -> str:
    """Get description for an event"""
    descriptions = {
        WebhookEvent.QUERY_COMPLETED: "Fired when a query is successfully completed",
        WebhookEvent.QUERY_FAILED: "Fired when a query fails",
        WebhookEvent.HEALTH_DEGRADED: "Fired when system health degrades",
        WebhookEvent.HEALTH_RECOVERED: "Fired when system health recovers",
        WebhookEvent.RATE_LIMIT_EXCEEDED: "Fired when rate limit is exceeded",
        WebhookEvent.ERROR_THRESHOLD: "Fired when error threshold is reached",
        WebhookEvent.SYSTEM_ALERT: "Fired for general system alerts"
    }
    return descriptions.get(event, "No description available")
