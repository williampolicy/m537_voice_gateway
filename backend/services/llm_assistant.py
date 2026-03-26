"""
M537 Voice Gateway - LLM Intent Assistant
Optional LLM-based intent classification as fallback
"""
import os
import logging
from typing import Optional, Dict, Any, Tuple, List
import json

logger = logging.getLogger(__name__)

# Available intents for LLM classification
AVAILABLE_INTENTS = {
    "count_projects": "查询项目总数和各优先级分布",
    "list_ports": "列出服务器监听的端口",
    "list_containers": "列出Docker容器状态",
    "system_status": "查询系统CPU、内存、磁盘使用率",
    "recent_errors": "查询最近的错误日志",
    "project_summary": "查询特定项目的介绍信息",
    "missing_readme": "查找缺少README的项目",
    "recent_updates": "查询最近更新的项目",
    "p0_health": "检查P0关键服务健康状态",
    "list_tmux": "列出tmux会话"
}


class LLMAssistant:
    """
    LLM-based intent assistant.
    Uses external LLM API when available, falls back to pattern matching.
    """

    def __init__(self):
        self.api_key = os.environ.get("OPENAI_API_KEY") or os.environ.get("ANTHROPIC_API_KEY")
        self.enabled = bool(self.api_key)
        self._http_client = None

        if self.enabled:
            logger.info("LLM Assistant enabled with API key")
        else:
            logger.info("LLM Assistant disabled (no API key configured)")

    async def classify_intent(
        self,
        transcript: str
    ) -> Tuple[Optional[str], float, Dict[str, Any]]:
        """
        Classify user intent using LLM.

        Args:
            transcript: User's speech transcript

        Returns:
            Tuple of (intent, confidence, params) or (None, 0.0, {}) if failed
        """
        if not self.enabled:
            return await self._fallback_classify(transcript)

        try:
            return await self._llm_classify(transcript)
        except Exception as e:
            logger.warning(f"LLM classification failed: {e}, using fallback")
            return await self._fallback_classify(transcript)

    async def _llm_classify(
        self,
        transcript: str
    ) -> Tuple[Optional[str], float, Dict[str, Any]]:
        """Classify using real LLM API"""
        # Build prompt
        intent_descriptions = "\n".join(
            f"- {intent}: {desc}"
            for intent, desc in AVAILABLE_INTENTS.items()
        )

        prompt = f"""你是一个意图分类助手。根据用户的语音输入，判断用户想要执行哪个操作。

可用的意图类型：
{intent_descriptions}

用户输入："{transcript}"

请以JSON格式回复，包含以下字段：
- intent: 匹配的意图名称（如果无法匹配则为null）
- confidence: 置信度（0.0-1.0）
- params: 提取的参数（如项目ID等）

仅返回JSON，不要其他内容。"""

        # Try Anthropic API first
        if os.environ.get("ANTHROPIC_API_KEY"):
            return await self._call_anthropic(prompt)

        # Try OpenAI API
        if os.environ.get("OPENAI_API_KEY"):
            return await self._call_openai(prompt)

        return None, 0.0, {}

    async def _call_anthropic(self, prompt: str) -> Tuple[Optional[str], float, Dict[str, Any]]:
        """Call Anthropic Claude API"""
        import httpx

        api_key = os.environ.get("ANTHROPIC_API_KEY")

        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json"
                },
                json={
                    "model": "claude-3-haiku-20240307",
                    "max_tokens": 256,
                    "messages": [{"role": "user", "content": prompt}]
                },
                timeout=5.0
            )

            if response.status_code == 200:
                data = response.json()
                content = data["content"][0]["text"]
                return self._parse_llm_response(content)
            else:
                logger.warning(f"Anthropic API error: {response.status_code}")
                return None, 0.0, {}

    async def _call_openai(self, prompt: str) -> Tuple[Optional[str], float, Dict[str, Any]]:
        """Call OpenAI API"""
        import httpx

        api_key = os.environ.get("OPENAI_API_KEY")

        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "gpt-3.5-turbo",
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 256,
                    "temperature": 0.3
                },
                timeout=5.0
            )

            if response.status_code == 200:
                data = response.json()
                content = data["choices"][0]["message"]["content"]
                return self._parse_llm_response(content)
            else:
                logger.warning(f"OpenAI API error: {response.status_code}")
                return None, 0.0, {}

    def _parse_llm_response(
        self,
        content: str
    ) -> Tuple[Optional[str], float, Dict[str, Any]]:
        """Parse LLM JSON response"""
        try:
            # Clean up response
            content = content.strip()
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]

            data = json.loads(content)
            intent = data.get("intent")
            confidence = float(data.get("confidence", 0.0))
            params = data.get("params", {})

            # Validate intent
            if intent and intent in AVAILABLE_INTENTS:
                return intent, min(confidence, 0.85), params  # Cap LLM confidence at 0.85

            return None, 0.0, {}
        except (json.JSONDecodeError, ValueError) as e:
            logger.warning(f"Failed to parse LLM response: {e}")
            return None, 0.0, {}

    async def _fallback_classify(
        self,
        transcript: str
    ) -> Tuple[Optional[str], float, Dict[str, Any]]:
        """
        Fallback classification using simple pattern matching.
        Used when LLM is not available.
        """
        transcript_lower = transcript.lower()

        # Simple keyword matching as fallback
        patterns = [
            (["docker", "容器"], "list_containers", 0.6),
            (["端口", "port", "监听"], "list_ports", 0.6),
            (["cpu", "内存", "磁盘", "负载"], "system_status", 0.6),
            (["错误", "error", "日志", "问题"], "recent_errors", 0.6),
            (["p0", "关键", "核心"], "p0_health", 0.6),
            (["tmux", "session", "会话"], "list_tmux", 0.6),
            (["readme", "文档"], "missing_readme", 0.6),
        ]

        for keywords, intent, confidence in patterns:
            if any(kw in transcript_lower for kw in keywords):
                return intent, confidence, {}

        return None, 0.0, {}


# Singleton instance
llm_assistant = LLMAssistant()
