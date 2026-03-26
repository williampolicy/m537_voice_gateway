"""
M537 Voice Gateway - Audit Logger
Security and operational audit logging
"""
from typing import Dict, Any, Optional
from datetime import datetime, timezone
from collections import deque
import threading
import json
import logging
import os

logger = logging.getLogger(__name__)


class AuditEvent:
    """Represents an audit log event"""

    def __init__(
        self,
        event_type: str,
        session_id: str,
        request_id: str,
        data: Dict[str, Any] = None,
        client_ip: str = None,
        user_agent: str = None
    ):
        self.timestamp = datetime.now(timezone.utc)
        self.event_type = event_type
        self.session_id = session_id
        self.request_id = request_id
        self.data = data or {}
        self.client_ip = client_ip
        self.user_agent = user_agent

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp.isoformat(),
            "event_type": self.event_type,
            "session_id": self.session_id,
            "request_id": self.request_id,
            "data": self.data,
            "client_ip": self.client_ip,
            "user_agent": self.user_agent
        }

    def to_log_line(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False)


class AuditLogger:
    """
    Audit logger for tracking security-relevant events.
    Maintains in-memory buffer with optional file output.
    """

    # Event types
    VOICE_QUERY = "voice_query"
    INTENT_RECOGNIZED = "intent_recognized"
    INTENT_NOT_RECOGNIZED = "intent_not_recognized"
    TOOL_EXECUTED = "tool_executed"
    TOOL_ERROR = "tool_error"
    RATE_LIMITED = "rate_limited"
    SESSION_CREATED = "session_created"
    LLM_FALLBACK = "llm_fallback"
    SECURITY_WARNING = "security_warning"

    def __init__(self, max_buffer_size: int = 10000, log_file: str = None):
        self.buffer: deque = deque(maxlen=max_buffer_size)
        self.log_file = log_file
        self._lock = threading.Lock()
        self._file_lock = threading.Lock()

        # Stats
        self.event_counts: Dict[str, int] = {}

        # Create log directory if needed
        if log_file:
            log_dir = os.path.dirname(log_file)
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir, exist_ok=True)

    def log(
        self,
        event_type: str,
        session_id: str = None,
        request_id: str = None,
        data: Dict[str, Any] = None,
        client_ip: str = None,
        user_agent: str = None
    ):
        """Log an audit event"""
        event = AuditEvent(
            event_type=event_type,
            session_id=session_id or "unknown",
            request_id=request_id or "unknown",
            data=data,
            client_ip=client_ip,
            user_agent=user_agent
        )

        with self._lock:
            self.buffer.append(event)
            self.event_counts[event_type] = self.event_counts.get(event_type, 0) + 1

        # Write to file if configured
        if self.log_file:
            self._write_to_file(event)

        # Also log to standard logger for monitoring
        logger.info(f"AUDIT: [{event_type}] {session_id}/{request_id}")

    def _write_to_file(self, event: AuditEvent):
        """Write event to log file"""
        try:
            with self._file_lock:
                with open(self.log_file, 'a', encoding='utf-8') as f:
                    f.write(event.to_log_line() + '\n')
        except Exception as e:
            logger.error(f"Failed to write audit log: {e}")

    def log_voice_query(
        self,
        session_id: str,
        request_id: str,
        transcript: str,
        client_ip: str = None
    ):
        """Log a voice query event"""
        # Truncate long transcripts for security
        safe_transcript = transcript[:200] if len(transcript) > 200 else transcript

        self.log(
            event_type=self.VOICE_QUERY,
            session_id=session_id,
            request_id=request_id,
            data={"transcript_length": len(transcript), "transcript_preview": safe_transcript[:50]},
            client_ip=client_ip
        )

    def log_intent(
        self,
        session_id: str,
        request_id: str,
        intent: str,
        confidence: float,
        recognized: bool = True
    ):
        """Log intent recognition event"""
        event_type = self.INTENT_RECOGNIZED if recognized else self.INTENT_NOT_RECOGNIZED
        self.log(
            event_type=event_type,
            session_id=session_id,
            request_id=request_id,
            data={"intent": intent, "confidence": confidence}
        )

    def log_tool_execution(
        self,
        session_id: str,
        request_id: str,
        tool: str,
        success: bool,
        cached: bool = False,
        duration_ms: float = 0,
        error: str = None
    ):
        """Log tool execution event"""
        event_type = self.TOOL_EXECUTED if success else self.TOOL_ERROR
        self.log(
            event_type=event_type,
            session_id=session_id,
            request_id=request_id,
            data={
                "tool": tool,
                "success": success,
                "cached": cached,
                "duration_ms": round(duration_ms, 2),
                "error": error
            }
        )

    def log_rate_limit(
        self,
        client_ip: str,
        request_id: str = None
    ):
        """Log rate limiting event"""
        self.log(
            event_type=self.RATE_LIMITED,
            request_id=request_id,
            client_ip=client_ip,
            data={"action": "blocked"}
        )

    def log_security_warning(
        self,
        session_id: str,
        request_id: str,
        warning_type: str,
        details: str = None,
        client_ip: str = None
    ):
        """Log security warning"""
        self.log(
            event_type=self.SECURITY_WARNING,
            session_id=session_id,
            request_id=request_id,
            data={"warning_type": warning_type, "details": details},
            client_ip=client_ip
        )
        # Also log at warning level
        logger.warning(f"SECURITY: {warning_type} - {details}")

    def get_recent_events(self, count: int = 100, event_type: str = None) -> list:
        """Get recent audit events"""
        with self._lock:
            events = list(self.buffer)

        if event_type:
            events = [e for e in events if e.event_type == event_type]

        return [e.to_dict() for e in events[-count:]]

    def get_stats(self) -> Dict[str, Any]:
        """Get audit statistics"""
        with self._lock:
            return {
                "total_events": sum(self.event_counts.values()),
                "events_by_type": dict(self.event_counts),
                "buffer_size": len(self.buffer),
                "log_file": self.log_file
            }


# Global audit logger instance
audit_logger = AuditLogger(
    max_buffer_size=10000,
    log_file="/app/logs/audit.log" if os.path.exists("/app") else None
)
