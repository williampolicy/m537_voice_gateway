"""
M537 Voice Gateway - Logging Configuration
Structured logging with rotation and multiple handlers
"""
import logging
import logging.handlers
import os
import sys
from typing import Optional
from pathlib import Path

from settings import settings


def setup_logging(
    log_dir: Optional[str] = None,
    log_level: Optional[str] = None,
    json_format: bool = False
):
    """
    Configure application logging with rotation and structured output.

    Args:
        log_dir: Directory for log files (default: logs/)
        log_level: Logging level (default: from settings)
        json_format: Use JSON format for structured logging
    """
    # Determine log directory
    if log_dir is None:
        log_dir = os.environ.get("LOG_DIR", "logs")

    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)

    # Determine log level
    level = getattr(logging, (log_level or settings.LOG_LEVEL).upper(), logging.INFO)

    # Clear existing handlers
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.setLevel(level)

    # Format strings
    if json_format:
        format_str = '{"time": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s", "message": "%(message)s"}'
    else:
        format_str = "%(asctime)s | %(levelname)-8s | %(name)-20s | %(message)s"

    date_format = "%Y-%m-%d %H:%M:%S"
    formatter = logging.Formatter(format_str, datefmt=date_format)

    # Console handler (stdout)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # Main log file with rotation
    main_log_file = log_path / "m537_gateway.log"
    file_handler = logging.handlers.RotatingFileHandler(
        main_log_file,
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=5,
        encoding="utf-8"
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)

    # Error log file (errors only)
    error_log_file = log_path / "m537_errors.log"
    error_handler = logging.handlers.RotatingFileHandler(
        error_log_file,
        maxBytes=5 * 1024 * 1024,  # 5 MB
        backupCount=3,
        encoding="utf-8"
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    root_logger.addHandler(error_handler)

    # Access log (requests)
    access_log_file = log_path / "m537_access.log"
    access_handler = logging.handlers.TimedRotatingFileHandler(
        access_log_file,
        when="midnight",
        interval=1,
        backupCount=30,  # Keep 30 days
        encoding="utf-8"
    )
    access_handler.setLevel(logging.INFO)
    access_handler.setFormatter(
        logging.Formatter("%(asctime)s | %(message)s", datefmt=date_format)
    )

    # Create access logger
    access_logger = logging.getLogger("m537.access")
    access_logger.addHandler(access_handler)
    access_logger.setLevel(logging.INFO)
    access_logger.propagate = False

    # Reduce noise from libraries
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)

    logging.info(f"Logging configured: level={level}, dir={log_path}")

    return root_logger


def get_access_logger():
    """Get the access logger for request logging"""
    return logging.getLogger("m537.access")


def log_request(method: str, path: str, status: int, duration_ms: float, client_ip: str = "-"):
    """Log an HTTP request in combined log format"""
    logger = get_access_logger()
    logger.info(f'{client_ip} "{method} {path}" {status} {duration_ms:.2f}ms')


class RequestLogMiddleware:
    """Middleware for logging HTTP requests"""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        import time
        start_time = time.time()

        # Capture response status
        status_code = 500

        async def send_wrapper(message):
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = message["status"]
            await send(message)

        try:
            await self.app(scope, receive, send_wrapper)
        finally:
            duration_ms = (time.time() - start_time) * 1000
            method = scope.get("method", "?")
            path = scope.get("path", "?")

            # Get client IP
            client = scope.get("client")
            client_ip = client[0] if client else "-"

            # Check for forwarded header
            headers = dict(scope.get("headers", []))
            if b"x-forwarded-for" in headers:
                client_ip = headers[b"x-forwarded-for"].decode().split(",")[0].strip()

            log_request(method, path, status_code, duration_ms, client_ip)
