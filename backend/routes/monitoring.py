"""
M537 Voice Gateway - Monitoring Routes
Uptime Kuma compatible monitoring endpoints
"""
from fastapi import APIRouter, Response
from datetime import datetime, timezone
import time
import os
import httpx
import asyncio
import logging

from settings import settings

router = APIRouter()
logger = logging.getLogger(__name__)

# Track startup time and last check
_startup_time = time.time()
_last_push_time = 0
_push_interval = 60  # seconds


async def push_heartbeat():
    """
    Push heartbeat to Uptime Kuma (if configured).
    Called by background task.
    """
    push_url = os.environ.get("UPTIME_KUMA_PUSH_URL")
    if not push_url:
        return

    global _last_push_time
    current_time = time.time()

    # Rate limit pushes
    if current_time - _last_push_time < _push_interval:
        return

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                push_url,
                params={
                    "status": "up",
                    "msg": "OK",
                    "ping": str(int((current_time - _startup_time) * 1000) % 100)
                },
                timeout=5.0
            )
            if response.status_code == 200:
                _last_push_time = current_time
                logger.debug("Heartbeat pushed to Uptime Kuma")
    except Exception as e:
        logger.warning(f"Failed to push heartbeat: {e}")


@router.get("/uptime")
async def uptime_check():
    """
    Uptime Kuma compatible health check endpoint.

    Returns simple OK response for HTTP(s) monitoring.
    Can also be used with HTTP(s) Keyword monitoring.
    """
    uptime = time.time() - _startup_time

    # Trigger push heartbeat (async, non-blocking)
    asyncio.create_task(push_heartbeat())

    return {
        "status": "OK",
        "service": "m537_voice_gateway",
        "version": settings.VERSION,
        "uptime_seconds": int(uptime),
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    }


@router.get("/uptime/simple")
async def uptime_simple():
    """
    Simple uptime endpoint for basic HTTP monitoring.
    Returns just "OK" for minimal overhead.
    """
    return Response(content="OK", media_type="text/plain")


@router.get("/uptime/push")
async def uptime_push_info():
    """
    Information about Uptime Kuma Push monitoring.
    """
    push_url = os.environ.get("UPTIME_KUMA_PUSH_URL", "")
    is_configured = bool(push_url)

    return {
        "push_configured": is_configured,
        "push_interval_seconds": _push_interval,
        "instructions": {
            "http_monitor": {
                "url": "https://voice.x1000.ai/api/uptime",
                "method": "GET",
                "expected_status": 200,
                "keyword": "OK"
            },
            "push_monitor": {
                "env_var": "UPTIME_KUMA_PUSH_URL",
                "example": "https://your-kuma.com/api/push/xxxxx",
                "note": "Set this environment variable to enable push monitoring"
            }
        }
    }
