"""
M537 Voice Gateway - Voice Query Routes
Main API endpoint for voice queries
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, field_validator
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone
import uuid
import logging
import time

from services.intent_parser import IntentParser
from services.query_executor import QueryExecutor
from services.response_builder import ResponseBuilder
from services.llm_assistant import llm_assistant
from services.session_manager import session_manager
from services.audit_logger import audit_logger
from routes.metrics import metrics_collector

router = APIRouter()
logger = logging.getLogger(__name__)

# Initialize services
intent_parser = IntentParser()
query_executor = QueryExecutor()
response_builder = ResponseBuilder()


class VoiceQueryRequest(BaseModel):
    """Voice query request model"""
    transcript: str = Field(..., min_length=1, max_length=500)
    session_id: Optional[str] = Field(None, max_length=100)
    context: Optional[Dict[str, Any]] = None

    @field_validator("transcript")
    @classmethod
    def sanitize_transcript(cls, v: str) -> str:
        """Remove potentially dangerous characters"""
        dangerous_chars = [";", "|", "&", "`", "$", "(", ")", "{", "}", "<", ">"]
        for char in dangerous_chars:
            v = v.replace(char, "")
        return v.strip()


class VoiceQueryResponse(BaseModel):
    """Voice query response model"""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None
    timestamp: str
    request_id: str


@router.post("/voice-query", response_model=VoiceQueryResponse)
async def voice_query(request: VoiceQueryRequest):
    """
    Main voice query endpoint

    Processes natural language queries and returns structured responses.
    """
    request_id = f"req_{uuid.uuid4().hex[:12]}"
    timestamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    logger.info(f"[{request_id}] Processing query: {request.transcript[:50]}...")
    start_time = time.time()
    llm_used = False

    # Audit log the query
    audit_logger.log_voice_query(
        session_id=request.session_id or request_id,
        request_id=request_id,
        transcript=request.transcript
    )

    # Get session context for multi-turn support
    session_id = request.session_id or request_id
    session_context = session_manager.get_follow_up_context(session_id)

    try:
        # Step 0: Resolve pronoun references (e.g., "它" -> "m537")
        resolved_project = session_manager.resolve_pronoun_reference(session_id, request.transcript)
        if resolved_project:
            logger.info(f"[{request_id}] Resolved pronoun to project: {resolved_project}")

        # Step 1: Parse intent (rule-based)
        intent, confidence, params = intent_parser.parse(request.transcript)

        # Apply resolved pronoun if no project_id in params
        if resolved_project and "project_id" not in params:
            if intent in ["project_summary"] or "项目" in request.transcript:
                params["project_id"] = resolved_project
                logger.info(f"[{request_id}] Applied resolved project: {resolved_project}")

        # Step 1b: Try LLM fallback if rule-based parsing failed
        if intent is None and llm_assistant.enabled:
            try:
                intent, confidence, params = await llm_assistant.classify_intent(request.transcript)
                llm_used = True
                if intent:
                    logger.info(f"[{request_id}] LLM classified intent: {intent} (confidence: {confidence})")
                    metrics_collector.record_llm_fallback(True)
                else:
                    metrics_collector.record_llm_fallback(False)
            except Exception as e:
                logger.warning(f"[{request_id}] LLM fallback failed: {e}")
                metrics_collector.record_llm_fallback(False)

        if intent is None:
            # Intent not recognized - provide context-aware suggestions
            duration = time.time() - start_time
            metrics_collector.record_request(False, duration, intent=None, tool=None)

            suggestions = intent_parser.get_suggestions(request.transcript)
            return VoiceQueryResponse(
                success=False,
                error={
                    "code": "INTENT_NOT_RECOGNIZED",
                    "message": "抱歉，我没有理解你的问题。请尝试以下查询方式：",
                    "suggestions": suggestions
                },
                timestamp=timestamp,
                request_id=request_id
            )

        # Step 2: Execute query
        result = query_executor.execute(intent, params)

        if not result["success"]:
            duration = time.time() - start_time
            metrics_collector.record_request(False, duration, intent=intent, tool=intent)
            metrics_collector.record_tool_error(intent)

            return VoiceQueryResponse(
                success=False,
                error={
                    "code": "EXECUTION_FAILED",
                    "message": f"查询执行失败：{result.get('error', '未知错误')}"
                },
                timestamp=timestamp,
                request_id=request_id
            )

        # Step 3: Build response
        answer_text = response_builder.build(intent, result["data"])

        duration = time.time() - start_time
        metrics_collector.record_request(True, duration, intent=intent, tool=intent)
        logger.info(f"[{request_id}] Query successful, intent: {intent}, duration: {duration*1000:.1f}ms")

        # Record conversation turn for context
        session_manager.record_turn(
            session_id=session_id,
            query=request.transcript,
            intent=intent,
            response=answer_text,
            data=result.get("data", {})
        )

        return VoiceQueryResponse(
            success=True,
            data={
                "answer_text": answer_text,
                "intent": intent,
                "confidence": confidence,
                "tool_used": intent,
                "raw_data": result["data"],
                "suggestions": intent_parser.get_related_suggestions(intent)
            },
            timestamp=timestamp,
            request_id=request_id
        )

    except Exception as e:
        duration = time.time() - start_time
        metrics_collector.record_request(False, duration, intent=None, tool=None)
        logger.error(f"[{request_id}] Error processing query: {e}")
        return VoiceQueryResponse(
            success=False,
            error={
                "code": "INTERNAL_ERROR",
                "message": "服务器内部错误，请稍后重试。"
            },
            timestamp=timestamp,
            request_id=request_id
        )
