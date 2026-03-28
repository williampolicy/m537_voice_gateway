"""
M537 Voice Gateway - Background Task Scheduler
Handles periodic background tasks
"""
import asyncio
import logging
from datetime import datetime, timezone
from typing import Callable, Dict, Any, List
import functools

logger = logging.getLogger(__name__)


class Task:
    """Represents a scheduled task"""

    def __init__(
        self,
        name: str,
        func: Callable,
        interval_seconds: int,
        run_immediately: bool = False
    ):
        self.name = name
        self.func = func
        self.interval = interval_seconds
        self.run_immediately = run_immediately
        self.last_run = None
        self.run_count = 0
        self.error_count = 0
        self.is_running = False


class BackgroundScheduler:
    """
    Background task scheduler for periodic tasks.
    Uses asyncio for non-blocking execution.
    """

    def __init__(self):
        self.tasks: Dict[str, Task] = {}
        self._running = False
        self._task_handles: List[asyncio.Task] = []

    def register(
        self,
        name: str,
        interval_seconds: int,
        run_immediately: bool = False
    ):
        """
        Decorator to register a background task.

        Usage:
            @scheduler.register("cleanup_cache", interval_seconds=300)
            async def cleanup_cache():
                ...
        """
        def decorator(func: Callable):
            self.tasks[name] = Task(
                name=name,
                func=func,
                interval_seconds=interval_seconds,
                run_immediately=run_immediately
            )
            logger.info(f"Registered background task: {name} (every {interval_seconds}s)")
            return func
        return decorator

    async def start(self):
        """Start the scheduler"""
        if self._running:
            logger.warning("Scheduler already running")
            return

        self._running = True
        logger.info(f"Starting background scheduler with {len(self.tasks)} tasks")

        for name, task in self.tasks.items():
            handle = asyncio.create_task(self._run_task_loop(task))
            self._task_handles.append(handle)

    async def stop(self):
        """Stop the scheduler"""
        self._running = False

        for handle in self._task_handles:
            handle.cancel()

        if self._task_handles:
            await asyncio.gather(*self._task_handles, return_exceptions=True)

        self._task_handles.clear()
        logger.info("Background scheduler stopped")

    async def _run_task_loop(self, task: Task):
        """Run a single task in a loop"""
        if task.run_immediately:
            await self._execute_task(task)

        while self._running:
            try:
                await asyncio.sleep(task.interval)
                if self._running:
                    await self._execute_task(task)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.exception(f"Error in task loop {task.name}: {e}")
                await asyncio.sleep(task.interval)

    async def _execute_task(self, task: Task):
        """Execute a single task"""
        if task.is_running:
            logger.warning(f"Task {task.name} is already running, skipping")
            return

        task.is_running = True
        start_time = datetime.now(timezone.utc)

        try:
            logger.debug(f"Running task: {task.name}")

            if asyncio.iscoroutinefunction(task.func):
                await task.func()
            else:
                await asyncio.get_event_loop().run_in_executor(None, task.func)

            task.run_count += 1
            task.last_run = start_time

            duration = (datetime.now(timezone.utc) - start_time).total_seconds()
            logger.debug(f"Task {task.name} completed in {duration:.2f}s")

        except Exception as e:
            task.error_count += 1
            logger.error(f"Task {task.name} failed: {e}")

        finally:
            task.is_running = False

    def get_stats(self) -> Dict[str, Any]:
        """Get scheduler statistics"""
        return {
            "running": self._running,
            "task_count": len(self.tasks),
            "tasks": {
                name: {
                    "interval_seconds": task.interval,
                    "run_count": task.run_count,
                    "error_count": task.error_count,
                    "last_run": task.last_run.isoformat() if task.last_run else None,
                    "is_running": task.is_running
                }
                for name, task in self.tasks.items()
            }
        }


# Global scheduler instance
scheduler = BackgroundScheduler()


# Register default tasks
@scheduler.register("cleanup_expired_cache", interval_seconds=300, run_immediately=False)
async def cleanup_expired_cache():
    """Clean up expired cache entries every 5 minutes"""
    from services.cache import query_cache
    query_cache.cleanup_expired()
    logger.debug("Cache cleanup completed")


@scheduler.register("cleanup_expired_sessions", interval_seconds=600, run_immediately=False)
async def cleanup_expired_sessions():
    """Clean up expired sessions every 10 minutes"""
    from services.session_manager import session_manager
    # Session manager handles cleanup internally
    stats = session_manager.get_stats()
    logger.debug(f"Session stats: {stats['active_sessions']} active sessions")


@scheduler.register("rotate_audit_logs", interval_seconds=86400, run_immediately=False)
async def rotate_audit_logs():
    """Rotate audit logs daily"""
    from services.audit_logger import audit_logger
    audit_logger.rotate()
    logger.info("Audit log rotation completed")


@scheduler.register("health_self_check", interval_seconds=60, run_immediately=True)
async def health_self_check():
    """Perform periodic self health check"""
    import psutil

    cpu = psutil.cpu_percent()
    mem = psutil.virtual_memory().percent
    disk = psutil.disk_usage("/").percent

    if cpu > 90:
        logger.warning(f"High CPU usage: {cpu}%")
    if mem > 90:
        logger.warning(f"High memory usage: {mem}%")
    if disk > 90:
        logger.warning(f"High disk usage: {disk}%")
