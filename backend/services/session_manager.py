"""
M537 Voice Gateway - Session Manager
Manages conversation context and session state for multi-turn dialogue
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone, timedelta
from collections import deque
import threading
import logging

logger = logging.getLogger(__name__)


class ConversationTurn:
    """Represents a single turn in the conversation"""

    def __init__(self, query: str, intent: str, response: str, data: Dict[str, Any] = None):
        self.query = query
        self.intent = intent
        self.response = response
        self.data = data or {}
        self.timestamp = datetime.now(timezone.utc)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "query": self.query,
            "intent": self.intent,
            "response": self.response,
            "data": self.data,
            "timestamp": self.timestamp.isoformat()
        }


class Session:
    """Represents a user session with conversation history"""

    def __init__(self, session_id: str, max_turns: int = 10):
        self.session_id = session_id
        self.history: deque = deque(maxlen=max_turns)
        self.created_at = datetime.now(timezone.utc)
        self.last_activity = self.created_at
        self.context: Dict[str, Any] = {}  # Persistent context within session

    def add_turn(self, query: str, intent: str, response: str, data: Dict[str, Any] = None):
        """Add a conversation turn"""
        turn = ConversationTurn(query, intent, response, data)
        self.history.append(turn)
        self.last_activity = datetime.now(timezone.utc)

        # Update context based on intent
        self._update_context(intent, data)

    def _update_context(self, intent: str, data: Dict[str, Any]):
        """Update session context based on the latest query"""
        if not data:
            return

        # Track last queried project
        if intent == "project_summary" and "project_id" in data:
            self.context["last_project"] = data.get("project_id")

        # Track focus areas
        if intent in ["system_status", "list_containers", "list_ports"]:
            self.context["focus"] = "system"
        elif intent in ["count_projects", "project_summary", "recent_updates"]:
            self.context["focus"] = "projects"
        elif intent in ["recent_errors", "p0_health"]:
            self.context["focus"] = "health"

        # Store last successful data for follow-up queries
        self.context["last_data"] = data
        self.context["last_intent"] = intent

    def get_last_intent(self) -> Optional[str]:
        """Get the last recognized intent"""
        if self.history:
            return self.history[-1].intent
        return None

    def get_last_project(self) -> Optional[str]:
        """Get the last queried project ID"""
        return self.context.get("last_project")

    def get_context(self) -> Dict[str, Any]:
        """Get current session context"""
        return {
            "session_id": self.session_id,
            "turn_count": len(self.history),
            "last_intent": self.context.get("last_intent"),
            "last_project": self.context.get("last_project"),
            "focus": self.context.get("focus"),
            "created_at": self.created_at.isoformat(),
            "last_activity": self.last_activity.isoformat()
        }

    def get_history_summary(self) -> List[Dict[str, Any]]:
        """Get summary of conversation history"""
        return [turn.to_dict() for turn in self.history]

    def is_expired(self, max_idle_minutes: int = 30) -> bool:
        """Check if session has expired"""
        idle_time = datetime.now(timezone.utc) - self.last_activity
        return idle_time > timedelta(minutes=max_idle_minutes)


class SessionManager:
    """Manages multiple user sessions"""

    def __init__(self, max_sessions: int = 1000, session_timeout_minutes: int = 30):
        self.sessions: Dict[str, Session] = {}
        self.max_sessions = max_sessions
        self.session_timeout = session_timeout_minutes
        self._lock = threading.Lock()

        # Stats
        self.total_sessions_created = 0
        self.total_turns_processed = 0

    def get_or_create_session(self, session_id: str) -> Session:
        """Get existing session or create new one"""
        with self._lock:
            if session_id in self.sessions:
                session = self.sessions[session_id]
                if not session.is_expired(self.session_timeout):
                    return session
                # Session expired, remove it
                del self.sessions[session_id]

            # Create new session
            self._cleanup_old_sessions()
            session = Session(session_id)
            self.sessions[session_id] = session
            self.total_sessions_created += 1

            logger.debug(f"Created new session: {session_id}")
            return session

    def record_turn(
        self,
        session_id: str,
        query: str,
        intent: str,
        response: str,
        data: Dict[str, Any] = None
    ):
        """Record a conversation turn"""
        session = self.get_or_create_session(session_id)
        session.add_turn(query, intent, response, data)
        self.total_turns_processed += 1

    def get_context(self, session_id: str) -> Dict[str, Any]:
        """Get session context"""
        with self._lock:
            if session_id in self.sessions:
                return self.sessions[session_id].get_context()
            return {}

    def resolve_pronoun_reference(self, session_id: str, query: str) -> Optional[str]:
        """
        Resolve pronoun references like "它" or "这个项目" to actual project IDs.
        Returns the resolved project ID or None.
        """
        with self._lock:
            if session_id not in self.sessions:
                return None

            session = self.sessions[session_id]

            # Check for pronoun references
            pronoun_patterns = ["它", "这个", "那个", "这个项目", "那个项目", "刚才的", "上一个"]

            query_lower = query.lower()
            for pattern in pronoun_patterns:
                if pattern in query_lower:
                    # Try to resolve to last queried project
                    last_project = session.get_last_project()
                    if last_project:
                        logger.debug(f"Resolved '{pattern}' to project: {last_project}")
                        return last_project

            return None

    def get_follow_up_context(self, session_id: str) -> Dict[str, Any]:
        """
        Get context for follow-up queries.
        Useful for understanding implicit references.
        """
        with self._lock:
            if session_id not in self.sessions:
                return {}

            session = self.sessions[session_id]
            return {
                "last_intent": session.context.get("last_intent"),
                "last_project": session.context.get("last_project"),
                "focus": session.context.get("focus"),
                "last_data": session.context.get("last_data")
            }

    def _cleanup_old_sessions(self):
        """Remove expired sessions"""
        # Already under lock
        expired = [
            sid for sid, session in self.sessions.items()
            if session.is_expired(self.session_timeout)
        ]

        for sid in expired:
            del self.sessions[sid]
            logger.debug(f"Cleaned up expired session: {sid}")

        # If still over limit, remove oldest
        if len(self.sessions) >= self.max_sessions:
            oldest = min(
                self.sessions.items(),
                key=lambda x: x[1].last_activity
            )
            del self.sessions[oldest[0]]
            logger.debug(f"Removed oldest session due to limit: {oldest[0]}")

    def get_stats(self) -> Dict[str, Any]:
        """Get session manager statistics"""
        with self._lock:
            return {
                "active_sessions": len(self.sessions),
                "total_sessions_created": self.total_sessions_created,
                "total_turns_processed": self.total_turns_processed,
                "max_sessions": self.max_sessions,
                "session_timeout_minutes": self.session_timeout
            }


# Global session manager instance
session_manager = SessionManager()
