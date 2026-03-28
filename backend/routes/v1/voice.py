"""
M537 Voice Gateway - Voice Query API v1
Enhanced voice query endpoint with additional features
"""
from fastapi import APIRouter, Request, Header, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone
import uuid
import logging

from services.intent_parser import IntentParser
from services.query_executor import QueryExecutor
from services.response_builder import ResponseBuilder
from services.session_manager import session_manager
from services.cache import query_cache
from services.audit_logger import audit_logger
from services.i18n import detect_language, t

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize services
intent_parser = IntentParser()
query_executor = QueryExecutor()
response_builder = ResponseBuilder()


class VoiceQueryRequest(BaseModel):
    """Voice query request model with validation"""
    transcript: str = Field(..., min_length=1, max_length=500, description="User's voice transcript")
    session_id: Optional[str] = Field(None, max_length=64, description="Session ID for multi-turn dialogue")
    context: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional context")
    language: Optional[str] = Field(None, description="Preferred language (zh-CN, en-US, ja-JP)")
    include_raw: Optional[bool] = Field(False, description="Include raw data in response")


class VoiceQueryResponse(BaseModel):
    """Voice query response model"""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None
    timestamp: str
    request_id: str
    api_version: str = "v1"


@router.post("/voice-query", response_model=VoiceQueryResponse)
async def voice_query_v1(
    request: VoiceQueryRequest,
    background_tasks: BackgroundTasks,
    http_request: Request,
    accept_language: Optional[str] = Header(None),
    x_request_id: Optional[str] = Header(None)
):
    """
    Enhanced voice query endpoint (v1).

    Features:
    - Multi-turn dialogue support
    - Language detection from Accept-Language header
    - Request ID tracking
    - Background audit logging
    """
    request_id = x_request_id or str(uuid.uuid4())
    timestamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    # Detect language
    language = request.language or detect_language({"accept-language": accept_language or ""})

    try:
        # Get session context
        session_context = {}
        if request.session_id:
            session_context = session_manager.get_context(request.session_id)

            # Resolve pronoun references
            resolved = session_manager.resolve_pronoun_reference(
                request.session_id,
                request.transcript
            )
            if resolved:
                request.transcript = request.transcript.replace("它", resolved)
                request.transcript = request.transcript.replace("这个项目", resolved)

        # Parse intent
        parse_result = intent_parser.parse(request.transcript)
        intent = parse_result.get("intent")
        confidence = parse_result.get("confidence", 0)
        params = parse_result.get("params", {})

        # Merge with context
        params.update(request.context or {})

        if not intent:
            return VoiceQueryResponse(
                success=False,
                error={
                    "code": "INTENT_NOT_RECOGNIZED",
                    "message": t("error.intent_not_recognized", language),
                    "suggestions": _get_suggestions(language)
                },
                timestamp=timestamp,
                request_id=request_id
            )

        # Execute query
        result = query_executor.execute(intent, params)

        if not result.get("success"):
            return VoiceQueryResponse(
                success=False,
                error={
                    "code": "EXECUTION_FAILED",
                    "message": t("error.execution_failed", language, error=result.get("error", "Unknown"))
                },
                timestamp=timestamp,
                request_id=request_id
            )

        # Build response
        answer_text = response_builder.build(intent, result.get("data", {}))

        # Record in session
        if request.session_id:
            session_manager.record_turn(
                request.session_id,
                request.transcript,
                intent,
                answer_text,
                result.get("data")
            )

        # Background audit logging
        background_tasks.add_task(
            audit_logger.log,
            event="voice_query_v1",
            data={
                "request_id": request_id,
                "intent": intent,
                "confidence": confidence,
                "cached": result.get("cached", False),
                "session_id": request.session_id,
                "language": language
            }
        )

        response_data = {
            "answer_text": answer_text,
            "intent": intent,
            "confidence": confidence,
            "tool_used": intent,
            "suggestions": _get_follow_up_suggestions(intent, language),
            "cached": result.get("cached", False),
            "language": language
        }

        if request.include_raw:
            response_data["raw_data"] = result.get("data")

        return VoiceQueryResponse(
            success=True,
            data=response_data,
            timestamp=timestamp,
            request_id=request_id
        )

    except Exception as e:
        logger.exception(f"Voice query error: {e}")
        return VoiceQueryResponse(
            success=False,
            error={
                "code": "INTERNAL_ERROR",
                "message": str(e)
            },
            timestamp=timestamp,
            request_id=request_id
        )


def _get_suggestions(language: str) -> List[str]:
    """Get query suggestions in the specified language"""
    suggestions = {
        "zh-CN": [
            "现在有多少个项目？",
            "系统状态怎么样？",
            "当前有哪些端口在监听？"
        ],
        "en-US": [
            "How many projects are there?",
            "What is the system status?",
            "Which ports are listening?"
        ],
        "ja-JP": [
            "プロジェクトはいくつありますか？",
            "システム状態はどうですか？",
            "どのポートがリッスンしていますか？"
        ]
    }
    return suggestions.get(language, suggestions["zh-CN"])


def _get_follow_up_suggestions(intent: str, language: str) -> List[str]:
    """Get follow-up suggestions based on intent"""
    follow_ups = {
        "count_projects": {
            "zh-CN": ["哪些是 P0 项目？", "最近更新了哪些项目？"],
            "en-US": ["Which are P0 projects?", "Which projects were recently updated?"],
            "ja-JP": ["P0プロジェクトはどれですか？", "最近更新されたプロジェクトは？"]
        },
        "system_status": {
            "zh-CN": ["磁盘空间够吗？", "有哪些容器在运行？"],
            "en-US": ["Is there enough disk space?", "Which containers are running?"],
            "ja-JP": ["ディスク容量は足りていますか？", "実行中のコンテナは？"]
        }
    }
    return follow_ups.get(intent, {}).get(language, [])
