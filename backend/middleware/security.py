"""
M537 Voice Gateway - Security Middleware
Comprehensive security headers and input validation
"""
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import re
import uuid
import logging
import html
from typing import Set

logger = logging.getLogger(__name__)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Adds comprehensive security headers to all responses.
    Implements OWASP recommended security headers.
    """

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        # Request ID for tracing
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        response.headers["X-Request-ID"] = request_id

        # Content Security Policy
        csp = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data:; "
            "font-src 'self'; "
            "connect-src 'self' wss: ws:; "
            "frame-ancestors 'none'; "
            "base-uri 'self'; "
            "form-action 'self'"
        )
        response.headers["Content-Security-Policy"] = csp

        # Prevent MIME type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"

        # XSS Protection (legacy browsers)
        response.headers["X-XSS-Protection"] = "1; mode=block"

        # Prevent clickjacking
        response.headers["X-Frame-Options"] = "DENY"

        # Referrer Policy
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Permissions Policy (disable sensitive APIs)
        response.headers["Permissions-Policy"] = (
            "geolocation=(), microphone=(), camera=(), "
            "payment=(), usb=(), magnetometer=(), "
            "gyroscope=(), accelerometer=()"
        )

        # Strict Transport Security (HSTS)
        # Only add for HTTPS requests
        if request.url.scheme == "https":
            response.headers["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains; preload"
            )

        # Cache control for API responses
        if request.url.path.startswith("/api/"):
            response.headers["Cache-Control"] = "no-store, max-age=0"
            response.headers["Pragma"] = "no-cache"

        return response


class InputSanitizationMiddleware(BaseHTTPMiddleware):
    """
    Sanitizes and validates input to prevent injection attacks.
    """

    # Dangerous patterns that may indicate attacks
    DANGEROUS_PATTERNS = [
        r'<script[^>]*>',           # Script tags
        r'javascript:',              # JavaScript protocol
        r'on\w+\s*=',               # Event handlers
        r'data:text/html',          # Data URLs with HTML
        r'expression\s*\(',         # CSS expressions
        r'<!--.*?-->',              # HTML comments (potential XSS)
        r'\${.*?}',                 # Template injection
        r'{{.*?}}',                 # Template injection
    ]

    # SQL injection patterns (for logging/alerting)
    SQL_PATTERNS = [
        r"'\s*or\s*'",
        r"'\s*;\s*drop",
        r"union\s+select",
        r"--\s*$",
    ]

    # Command injection patterns
    CMD_PATTERNS = [
        r'[;&|`$]',                 # Shell metacharacters
        r'\$\(',                    # Command substitution
        r'`[^`]+`',                 # Backtick command
    ]

    def __init__(self, app, max_body_size: int = 1024 * 1024):  # 1MB default
        super().__init__(app)
        self.max_body_size = max_body_size
        self.dangerous_re = [re.compile(p, re.IGNORECASE) for p in self.DANGEROUS_PATTERNS]
        self.sql_re = [re.compile(p, re.IGNORECASE) for p in self.SQL_PATTERNS]
        self.cmd_re = [re.compile(p) for p in self.CMD_PATTERNS]

    async def dispatch(self, request: Request, call_next):
        # Check content length
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > self.max_body_size:
            logger.warning(f"Request body too large from {request.client.host}")
            return JSONResponse(
                status_code=413,
                content={
                    "success": False,
                    "error": {
                        "code": "PAYLOAD_TOO_LARGE",
                        "message": "请求体过大"
                    }
                }
            )

        # Validate and sanitize path
        if self._is_path_suspicious(request.url.path):
            logger.warning(f"Suspicious path from {request.client.host}: {request.url.path}")
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "error": {
                        "code": "INVALID_PATH",
                        "message": "无效的请求路径"
                    }
                }
            )

        # Check query parameters for injection
        for key, value in request.query_params.items():
            if self._contains_dangerous_pattern(value):
                logger.warning(f"Dangerous query param from {request.client.host}: {key}={value[:50]}")
                return JSONResponse(
                    status_code=400,
                    content={
                        "success": False,
                        "error": {
                            "code": "INVALID_INPUT",
                            "message": "请求包含非法字符"
                        }
                    }
                )

        return await call_next(request)

    def _is_path_suspicious(self, path: str) -> bool:
        """Check if path contains path traversal attempts"""
        suspicious_patterns = [
            '..',           # Directory traversal
            '%2e%2e',       # URL encoded ..
            '%252e',        # Double encoded .
            '///',          # Multiple slashes
            '\x00',         # Null byte
        ]
        path_lower = path.lower()
        return any(p in path_lower for p in suspicious_patterns)

    def _contains_dangerous_pattern(self, value: str) -> bool:
        """Check if value contains dangerous patterns"""
        if not value:
            return False

        for pattern in self.dangerous_re:
            if pattern.search(value):
                return True

        return False


class InputValidationMiddleware(BaseHTTPMiddleware):
    """
    Validates input fields specific to the voice gateway API.
    """

    MAX_TRANSCRIPT_LENGTH = 500
    MAX_SESSION_ID_LENGTH = 64
    VALID_SESSION_ID_PATTERN = re.compile(r'^[a-zA-Z0-9_-]+$')

    async def dispatch(self, request: Request, call_next):
        # Only validate POST to voice-query endpoint
        if request.method == "POST" and "/voice-query" in request.url.path:
            try:
                body = await request.body()
                if body:
                    import json
                    data = json.loads(body)

                    # Validate transcript
                    transcript = data.get("transcript", "")
                    if len(transcript) > self.MAX_TRANSCRIPT_LENGTH:
                        return JSONResponse(
                            status_code=422,
                            content={
                                "success": False,
                                "error": {
                                    "code": "VALIDATION_ERROR",
                                    "message": f"transcript 长度不能超过 {self.MAX_TRANSCRIPT_LENGTH} 字符"
                                }
                            }
                        )

                    # Validate session_id if provided
                    session_id = data.get("session_id")
                    if session_id:
                        if len(session_id) > self.MAX_SESSION_ID_LENGTH:
                            return JSONResponse(
                                status_code=422,
                                content={
                                    "success": False,
                                    "error": {
                                        "code": "VALIDATION_ERROR",
                                        "message": "session_id 过长"
                                    }
                                }
                            )
                        if not self.VALID_SESSION_ID_PATTERN.match(session_id):
                            return JSONResponse(
                                status_code=422,
                                content={
                                    "success": False,
                                    "error": {
                                        "code": "VALIDATION_ERROR",
                                        "message": "session_id 包含非法字符"
                                    }
                                }
                            )

            except json.JSONDecodeError:
                return JSONResponse(
                    status_code=422,
                    content={
                        "success": False,
                        "error": {
                            "code": "INVALID_JSON",
                            "message": "无效的 JSON 格式"
                        }
                    }
                )
            except Exception as e:
                logger.error(f"Input validation error: {e}")

        return await call_next(request)


def sanitize_string(s: str) -> str:
    """
    Sanitize a string by escaping HTML entities.
    Use for any user-provided content that will be displayed.
    """
    if not s:
        return s
    return html.escape(s)


def is_safe_project_id(project_id: str) -> bool:
    """
    Validate project ID to prevent path traversal.
    """
    if not project_id:
        return False

    # Only allow alphanumeric, underscore, and hyphen
    if not re.match(r'^[a-zA-Z0-9_-]+$', project_id):
        return False

    # No path components
    if '/' in project_id or '\\' in project_id:
        return False

    # No special directory names
    if project_id in ('.', '..'):
        return False

    return True


def log_security_event(
    event_type: str,
    request: Request,
    details: str = None,
    severity: str = "warning"
):
    """
    Log security-related events for monitoring.
    """
    client_ip = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "unknown")

    log_data = {
        "event": event_type,
        "client_ip": client_ip,
        "path": str(request.url.path),
        "method": request.method,
        "user_agent": user_agent[:100],
        "details": details
    }

    log_func = getattr(logger, severity, logger.warning)
    log_func(f"Security event: {log_data}")
