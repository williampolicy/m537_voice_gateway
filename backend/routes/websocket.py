"""
M537 Voice Gateway - WebSocket Routes
Real-time status updates via WebSocket
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List, Dict, Any
import asyncio
import logging
import json
from datetime import datetime, timezone

from tools.system_status import SystemStatusTool
from tools.list_containers import ListContainersTool
from tools.uptime_info import UptimeInfoTool
from routes.metrics import metrics_collector

router = APIRouter()
logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manage WebSocket connections"""

    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket):
        """Accept new WebSocket connection"""
        await websocket.accept()
        async with self._lock:
            self.active_connections.append(websocket)
        logger.info(f"WebSocket connected. Total: {len(self.active_connections)}")

    async def disconnect(self, websocket: WebSocket):
        """Remove WebSocket connection"""
        async with self._lock:
            if websocket in self.active_connections:
                self.active_connections.remove(websocket)
        logger.info(f"WebSocket disconnected. Total: {len(self.active_connections)}")

    async def broadcast(self, message: Dict[str, Any]):
        """Broadcast message to all connected clients"""
        if not self.active_connections:
            return

        disconnected = []
        message_json = json.dumps(message, ensure_ascii=False)

        for connection in self.active_connections:
            try:
                await connection.send_text(message_json)
            except Exception as e:
                logger.warning(f"Failed to send to WebSocket: {e}")
                disconnected.append(connection)

        # Clean up disconnected
        for conn in disconnected:
            await self.disconnect(conn)

    @property
    def connection_count(self) -> int:
        return len(self.active_connections)


# Global connection manager
manager = ConnectionManager()

# Tools for status updates
system_status_tool = SystemStatusTool()
containers_tool = ListContainersTool()


async def get_system_snapshot() -> Dict[str, Any]:
    """Get current system status snapshot"""
    try:
        # Get system status
        system_data = system_status_tool.execute({})

        # Get container status
        container_data = containers_tool.execute({})

        # Get uptime
        try:
            uptime_tool = UptimeInfoTool()
            uptime_data = uptime_tool.execute({})
        except Exception:
            uptime_data = {"success": False}

        # Get metrics
        metrics = metrics_collector.get_json_metrics()

        return {
            "type": "system_status",
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "data": {
                "system": {
                    "cpu": system_data.get("cpu", 0),
                    "memory": system_data.get("memory", 0),
                    "disk": system_data.get("disk", 0),
                    "warning": system_data.get("warning", "")
                },
                "containers": {
                    "running": container_data.get("running", 0),
                    "stopped": container_data.get("stopped", 0),
                    "total": container_data.get("running", 0) + container_data.get("stopped", 0)
                },
                "uptime": uptime_data.get("uptime", {}).get("human_readable", "未知") if uptime_data.get("success") else "未知",
                "load": uptime_data.get("load_average", {}) if uptime_data.get("success") else {},
                "metrics": {
                    "requests_total": metrics.get("requests", {}).get("total", 0),
                    "success_rate": metrics.get("requests", {}).get("success_rate", "0%"),
                    "cache_hit_rate": metrics.get("cache", {}).get("hit_rate", "0%")
                },
                "websocket_clients": manager.connection_count
            }
        }
    except Exception as e:
        logger.error(f"Error getting system snapshot: {e}")
        return {
            "type": "error",
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "error": str(e)
        }


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time updates.

    Sends system status updates every 5 seconds.
    """
    await manager.connect(websocket)

    try:
        # Send initial status immediately
        initial_status = await get_system_snapshot()
        await websocket.send_text(json.dumps(initial_status, ensure_ascii=False))

        # Keep connection alive and send updates
        while True:
            try:
                # Wait for messages or timeout
                data = await asyncio.wait_for(
                    websocket.receive_text(),
                    timeout=5.0  # Send update every 5 seconds
                )

                # Handle client messages
                try:
                    message = json.loads(data)
                    if message.get("type") == "ping":
                        await websocket.send_text(json.dumps({"type": "pong"}))
                    elif message.get("type") == "refresh":
                        # Client requested immediate refresh
                        status = await get_system_snapshot()
                        await websocket.send_text(json.dumps(status, ensure_ascii=False))
                except json.JSONDecodeError:
                    pass

            except asyncio.TimeoutError:
                # Timeout - send periodic update
                status = await get_system_snapshot()
                await websocket.send_text(json.dumps(status, ensure_ascii=False))

    except WebSocketDisconnect:
        await manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await manager.disconnect(websocket)


@router.websocket("/ws/metrics")
async def websocket_metrics_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for metrics-only updates.

    Lighter weight, sends only metrics every 3 seconds.
    """
    await manager.connect(websocket)

    try:
        while True:
            try:
                # Wait for messages or timeout
                data = await asyncio.wait_for(
                    websocket.receive_text(),
                    timeout=3.0
                )

                if data == "ping":
                    await websocket.send_text("pong")

            except asyncio.TimeoutError:
                # Send metrics update
                metrics = metrics_collector.get_json_metrics()
                message = {
                    "type": "metrics",
                    "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
                    "data": metrics
                }
                await websocket.send_text(json.dumps(message, ensure_ascii=False))

    except WebSocketDisconnect:
        await manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket metrics error: {e}")
        await manager.disconnect(websocket)


@router.get("/ws/stats")
async def websocket_stats():
    """Get WebSocket connection statistics"""
    return {
        "active_connections": manager.connection_count,
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    }
