"""
M537 Voice Gateway - Error Tracking
Centralized error tracking and reporting
"""
import os
import logging
import traceback
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from collections import deque
import threading

logger = logging.getLogger(__name__)

# Configuration
SENTRY_DSN = os.environ.get("SENTRY_DSN", "")
ERROR_TRACKING_ENABLED = bool(SENTRY_DSN) or os.environ.get("ERROR_TRACKING", "true").lower() == "true"


class ErrorEntry:
    """Represents a tracked error"""

    def __init__(
        self,
        exception: Exception,
        context: Optional[Dict[str, Any]] = None,
        user_info: Optional[Dict[str, Any]] = None
    ):
        self.timestamp = datetime.now(timezone.utc)
        self.exception_type = type(exception).__name__
        self.exception_message = str(exception)
        self.traceback = traceback.format_exc()
        self.context = context or {}
        self.user_info = user_info or {}
        self.fingerprint = self._generate_fingerprint()

    def _generate_fingerprint(self) -> str:
        """Generate a unique fingerprint for error grouping"""
        import hashlib
        key = f"{self.exception_type}:{self.exception_message}"
        return hashlib.md5(key.encode()).hexdigest()[:12]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp.isoformat(),
            "type": self.exception_type,
            "message": self.exception_message,
            "fingerprint": self.fingerprint,
            "context": self.context,
            "user_info": self.user_info
        }


class ErrorTracker:
    """
    In-memory error tracking with optional Sentry integration.
    Provides error aggregation, rate limiting, and reporting.
    """

    def __init__(self, max_errors: int = 1000):
        self.errors: deque = deque(maxlen=max_errors)
        self.error_counts: Dict[str, int] = {}
        self._lock = threading.Lock()
        self._sentry_initialized = False

        # Initialize Sentry if configured
        self._init_sentry()

    def _init_sentry(self):
        """Initialize Sentry SDK if DSN is provided"""
        if not SENTRY_DSN:
            return

        try:
            import sentry_sdk
            from sentry_sdk.integrations.fastapi import FastApiIntegration
            from sentry_sdk.integrations.starlette import StarletteIntegration

            sentry_sdk.init(
                dsn=SENTRY_DSN,
                environment=os.environ.get("ENVIRONMENT", "development"),
                release=f"m537-voice-gateway@1.0.0",
                traces_sample_rate=0.1,
                integrations=[
                    FastApiIntegration(),
                    StarletteIntegration(),
                ]
            )
            self._sentry_initialized = True
            logger.info("Sentry error tracking initialized")
        except ImportError:
            logger.warning("Sentry SDK not installed")
        except Exception as e:
            logger.error(f"Failed to initialize Sentry: {e}")

    def capture(
        self,
        exception: Exception,
        context: Optional[Dict[str, Any]] = None,
        user_info: Optional[Dict[str, Any]] = None,
        level: str = "error"
    ) -> str:
        """
        Capture and track an exception.

        Returns:
            Error fingerprint for reference
        """
        entry = ErrorEntry(exception, context, user_info)

        with self._lock:
            self.errors.append(entry)
            self.error_counts[entry.fingerprint] = self.error_counts.get(entry.fingerprint, 0) + 1

        # Log the error
        log_method = getattr(logger, level, logger.error)
        log_method(
            f"Error captured: {entry.exception_type}: {entry.exception_message}",
            extra={"fingerprint": entry.fingerprint, "context": context}
        )

        # Send to Sentry if available
        if self._sentry_initialized:
            try:
                import sentry_sdk
                with sentry_sdk.push_scope() as scope:
                    if context:
                        for key, value in context.items():
                            scope.set_extra(key, value)
                    if user_info:
                        scope.set_user(user_info)
                    sentry_sdk.capture_exception(exception)
            except Exception:
                pass

        return entry.fingerprint

    def get_recent_errors(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get recent errors"""
        with self._lock:
            errors = list(self.errors)[-limit:]
            return [e.to_dict() for e in reversed(errors)]

    def get_error_summary(self) -> Dict[str, Any]:
        """Get error summary statistics"""
        with self._lock:
            if not self.errors:
                return {
                    "total_errors": 0,
                    "unique_errors": 0,
                    "top_errors": []
                }

            # Get top errors by count
            top_errors = sorted(
                self.error_counts.items(),
                key=lambda x: x[1],
                reverse=True
            )[:10]

            # Find error details for top errors
            top_error_details = []
            for fingerprint, count in top_errors:
                # Find most recent error with this fingerprint
                for error in reversed(list(self.errors)):
                    if error.fingerprint == fingerprint:
                        top_error_details.append({
                            "fingerprint": fingerprint,
                            "type": error.exception_type,
                            "message": error.exception_message[:100],
                            "count": count,
                            "last_seen": error.timestamp.isoformat()
                        })
                        break

            return {
                "total_errors": len(self.errors),
                "unique_errors": len(self.error_counts),
                "top_errors": top_error_details
            }

    def clear(self):
        """Clear all tracked errors"""
        with self._lock:
            self.errors.clear()
            self.error_counts.clear()


# Global error tracker instance
error_tracker = ErrorTracker()


def capture_exception(
    exception: Exception,
    context: Optional[Dict[str, Any]] = None,
    user_info: Optional[Dict[str, Any]] = None
) -> str:
    """Convenience function to capture an exception"""
    return error_tracker.capture(exception, context, user_info)


# FastAPI exception handler
async def error_handler_middleware(request, exc):
    """Handle unhandled exceptions"""
    from fastapi.responses import JSONResponse

    fingerprint = capture_exception(
        exc,
        context={
            "path": str(request.url.path),
            "method": request.method,
            "query_params": dict(request.query_params)
        }
    )

    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred",
                "reference": fingerprint
            }
        }
    )
