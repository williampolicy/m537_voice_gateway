"""
M537 Voice Gateway - LLM Assistant Tests
"""
import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))


class TestLLMAssistant:
    """LLM Assistant tests"""

    def test_assistant_disabled_without_api_key(self):
        """Assistant should be disabled without API key"""
        # Clear any existing API keys for this test
        orig_openai = os.environ.pop("OPENAI_API_KEY", None)
        orig_anthropic = os.environ.pop("ANTHROPIC_API_KEY", None)

        try:
            # Re-import to get fresh instance
            from importlib import reload
            import services.llm_assistant
            reload(services.llm_assistant)

            from services.llm_assistant import LLMAssistant
            assistant = LLMAssistant()
            assert assistant.enabled == False
        finally:
            # Restore original values
            if orig_openai:
                os.environ["OPENAI_API_KEY"] = orig_openai
            if orig_anthropic:
                os.environ["ANTHROPIC_API_KEY"] = orig_anthropic

    @pytest.mark.asyncio
    async def test_fallback_classify_containers(self):
        """Fallback should classify container-related queries"""
        from services.llm_assistant import LLMAssistant
        assistant = LLMAssistant()
        assistant.enabled = False  # Force fallback

        intent, confidence, params = await assistant._fallback_classify("docker容器状态")
        assert intent == "list_containers"
        assert confidence == 0.6

    @pytest.mark.asyncio
    async def test_fallback_classify_system(self):
        """Fallback should classify system-related queries"""
        from services.llm_assistant import LLMAssistant
        assistant = LLMAssistant()
        assistant.enabled = False

        intent, confidence, params = await assistant._fallback_classify("服务器cpu负载如何")
        assert intent == "system_status"
        assert confidence == 0.6

    @pytest.mark.asyncio
    async def test_fallback_classify_unknown(self):
        """Fallback should return None for unknown queries"""
        from services.llm_assistant import LLMAssistant
        assistant = LLMAssistant()
        assistant.enabled = False

        intent, confidence, params = await assistant._fallback_classify("今天天气怎么样")
        assert intent is None
        assert confidence == 0.0

    def test_parse_llm_response_valid(self):
        """Should parse valid JSON response"""
        from services.llm_assistant import LLMAssistant
        assistant = LLMAssistant()

        response = '{"intent": "count_projects", "confidence": 0.9, "params": {}}'
        intent, confidence, params = assistant._parse_llm_response(response)

        assert intent == "count_projects"
        assert confidence == 0.85  # Capped at 0.85
        assert params == {}

    def test_parse_llm_response_with_code_block(self):
        """Should parse JSON wrapped in code block"""
        from services.llm_assistant import LLMAssistant
        assistant = LLMAssistant()

        response = '```json\n{"intent": "system_status", "confidence": 0.8, "params": {}}\n```'
        intent, confidence, params = assistant._parse_llm_response(response)

        assert intent == "system_status"
        assert confidence == 0.8

    def test_parse_llm_response_invalid_intent(self):
        """Should return None for invalid intent"""
        from services.llm_assistant import LLMAssistant
        assistant = LLMAssistant()

        response = '{"intent": "invalid_intent", "confidence": 0.9, "params": {}}'
        intent, confidence, params = assistant._parse_llm_response(response)

        assert intent is None

    def test_parse_llm_response_invalid_json(self):
        """Should handle invalid JSON gracefully"""
        from services.llm_assistant import LLMAssistant
        assistant = LLMAssistant()

        response = 'not a json response'
        intent, confidence, params = assistant._parse_llm_response(response)

        assert intent is None
        assert confidence == 0.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
