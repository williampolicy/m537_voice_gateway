"""
M537 Voice Gateway - Graceful Shutdown
Proper connection draining and resource cleanup
"""
import asyncio
import signal
import logging
from datetime import datetime, timezone
from typing import Set, Callable, Awaitable, Optional
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)


class GracefulShutdown:
    """
    Manages graceful shutdown with connection draining.

    Features:
    - Tracks active requests/connections
    - Waits for in-flight requests to complete
    - Timeout-based forced shutdown
    - Cleanup callbacks for resources
    """

    def __init__(
        self,
        shutdown_timeout: float = 30.0,
        drain_timeout: float = 10.0
    ):
        self.shutdown_timeout = shutdown_timeout
        self.drain_timeout = drain_timeout
        self._active_requests: Set[str] = set()
        self._cleanup_callbacks: list = []
        self._is_shutting_down = False
        self._shutdown_event = asyncio.Event()
        self._request_counter = 0
        self._lock = asyncio.Lock()

    @property
    def is_shutting_down(self) -> bool:
        return self._is_shutting_down

    @property
    def active_request_count(self) -> int:
        return len(self._active_requests)

    async def register_request(self) -> str:
        """Register a new active request"""
        async with self._lock:
            self._request_counter += 1
            request_id = f"req_{self._request_counter}"
            self._active_requests.add(request_id)
            return request_id

    async def unregister_request(self, request_id: str):
        """Unregister a completed request"""
        async with self._lock:
            self._active_requests.discard(request_id)

    @asynccontextmanager
    async def track_request(self):
        """Context manager to track request lifecycle"""
        if self._is_shutting_down:
            raise ShutdownInProgressError("Server is shutting down")

        request_id = await self.register_request()
        try:
            yield request_id
        finally:
            await self.unregister_request(request_id)

    def add_cleanup_callback(
        self,
        callback: Callable[[], Awaitable[None]],
        name: Optional[str] = None
    ):
        """Add a cleanup callback to run during shutdown"""
        self._cleanup_callbacks.append({
            "callback": callback,
            "name": name or callback.__name__
        })

    async def _drain_connections(self) -> bool:
        """Wait for active connections to complete"""
        logger.info(f"Draining {self.active_request_count} active requests...")

        start_time = asyncio.get_event_loop().time()
        while self.active_request_count > 0:
            elapsed = asyncio.get_event_loop().time() - start_time
            if elapsed >= self.drain_timeout:
                logger.warning(
                    f"Drain timeout reached with {self.active_request_count} "
                    f"requests still active"
                )
                return False

            await asyncio.sleep(0.1)

        logger.info("All requests drained successfully")
        return True

    async def _run_cleanup_callbacks(self):
        """Run all registered cleanup callbacks"""
        for item in self._cleanup_callbacks:
            name = item["name"]
            callback = item["callback"]
            try:
                logger.info(f"Running cleanup: {name}")
                await asyncio.wait_for(callback(), timeout=5.0)
                logger.info(f"Cleanup completed: {name}")
            except asyncio.TimeoutError:
                logger.error(f"Cleanup timeout: {name}")
            except Exception as e:
                logger.error(f"Cleanup error ({name}): {e}")

    async def shutdown(self):
        """Initiate graceful shutdown"""
        if self._is_shutting_down:
            logger.warning("Shutdown already in progress")
            return

        self._is_shutting_down = True
        logger.info("Initiating graceful shutdown...")

        shutdown_start = datetime.now(timezone.utc)

        # Phase 1: Stop accepting new requests (handled by middleware)
        logger.info("Phase 1: Stopped accepting new requests")

        # Phase 2: Drain existing connections
        logger.info("Phase 2: Draining active connections")
        drain_success = await self._drain_connections()

        # Phase 3: Run cleanup callbacks
        logger.info("Phase 3: Running cleanup callbacks")
        await self._run_cleanup_callbacks()

        # Phase 4: Signal completion
        self._shutdown_event.set()

        duration = (datetime.now(timezone.utc) - shutdown_start).total_seconds()
        if drain_success:
            logger.info(f"Graceful shutdown completed in {duration:.2f}s")
        else:
            logger.warning(
                f"Shutdown completed with timeout in {duration:.2f}s "
                f"({self.active_request_count} requests dropped)"
            )

    async def wait_for_shutdown(self):
        """Wait for shutdown to complete"""
        await self._shutdown_event.wait()

    def get_status(self) -> dict:
        """Get current shutdown status"""
        return {
            "is_shutting_down": self._is_shutting_down,
            "active_requests": self.active_request_count,
            "pending_cleanups": len(self._cleanup_callbacks)
        }


class ShutdownInProgressError(Exception):
    """Raised when server is shutting down"""
    pass


# Global instance
shutdown_manager = GracefulShutdown()


def setup_signal_handlers(shutdown_callback: Callable):
    """
    Setup signal handlers for graceful shutdown.
    Call this during application startup.
    """
    loop = asyncio.get_event_loop()

    def handle_signal(sig):
        logger.info(f"Received signal {sig.name}")
        asyncio.create_task(shutdown_callback())

    for sig in (signal.SIGTERM, signal.SIGINT):
        try:
            loop.add_signal_handler(sig, lambda s=sig: handle_signal(s))
            logger.info(f"Registered handler for {sig.name}")
        except NotImplementedError:
            # Windows doesn't support add_signal_handler
            signal.signal(sig, lambda s, f: handle_signal(signal.Signals(s)))


class GracefulShutdownMiddleware:
    """
    ASGI middleware for graceful shutdown.
    Tracks active requests and rejects new ones during shutdown.
    """

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        # Check if shutting down
        if shutdown_manager.is_shutting_down:
            # Return 503 Service Unavailable
            await send({
                "type": "http.response.start",
                "status": 503,
                "headers": [
                    (b"content-type", b"application/json"),
                    (b"retry-after", b"30"),
                    (b"connection", b"close")
                ]
            })
            await send({
                "type": "http.response.body",
                "body": b'{"error": {"code": "SERVICE_UNAVAILABLE", "message": "Server is shutting down"}}'
            })
            return

        # Track request
        try:
            async with shutdown_manager.track_request():
                await self.app(scope, receive, send)
        except ShutdownInProgressError:
            await send({
                "type": "http.response.start",
                "status": 503,
                "headers": [(b"content-type", b"application/json")]
            })
            await send({
                "type": "http.response.body",
                "body": b'{"error": {"code": "SHUTDOWN_IN_PROGRESS", "message": "Server is shutting down"}}'
            })
