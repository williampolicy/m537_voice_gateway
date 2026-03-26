"""
M537 Voice Gateway - Integration Tests
端到端集成测试
"""
import pytest
import sys
import os

# 添加 backend 到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))


class TestEndToEnd:
    """端到端集成测试"""

    def test_full_query_flow_count_projects(self):
        """完整查询流程测试 - 项目数量"""
        # 1. 模拟语音输入
        transcript = "现在有多少个项目"

        # 2. 意图解析
        from services.intent_parser import IntentParser
        parser = IntentParser()
        intent, confidence, params = parser.parse(transcript)
        assert intent == "count_projects"
        assert confidence >= 0.9

        # 3. 查询执行
        from services.query_executor import QueryExecutor
        executor = QueryExecutor()
        result = executor.execute(intent, params)
        assert result["success"] == True
        assert "total" in result["data"]

        # 4. 响应构建
        from services.response_builder import ResponseBuilder
        builder = ResponseBuilder()
        answer = builder.build(intent, result["data"])
        assert "项目" in answer
        assert isinstance(answer, str)

    def test_full_query_flow_system_status(self):
        """完整查询流程测试 - 系统状态"""
        transcript = "系统状态怎么样"

        from services.intent_parser import IntentParser
        parser = IntentParser()
        intent, confidence, params = parser.parse(transcript)
        assert intent == "system_status"

        from services.query_executor import QueryExecutor
        executor = QueryExecutor()
        result = executor.execute(intent, params)
        assert result["success"] == True
        assert "cpu" in result["data"]

        from services.response_builder import ResponseBuilder
        builder = ResponseBuilder()
        answer = builder.build(intent, result["data"])
        assert "CPU" in answer or "cpu" in answer.lower()

    def test_full_query_flow_project_summary(self):
        """完整查询流程测试 - 项目摘要"""
        transcript = "m537是什么项目"

        from services.intent_parser import IntentParser
        parser = IntentParser()
        intent, confidence, params = parser.parse(transcript)
        assert intent == "project_summary"
        assert params.get("project_id") == "m537"

        from services.query_executor import QueryExecutor
        executor = QueryExecutor()
        result = executor.execute(intent, params)
        assert result["success"] == True

        from services.response_builder import ResponseBuilder
        builder = ResponseBuilder()
        answer = builder.build(intent, result["data"])
        assert isinstance(answer, str)

    def test_unknown_intent_flow(self):
        """未知意图处理流程"""
        transcript = "今天天气怎么样"

        from services.intent_parser import IntentParser
        parser = IntentParser()
        intent, confidence, params = parser.parse(transcript)
        assert intent is None

        from services.response_builder import ResponseBuilder
        builder = ResponseBuilder()
        suggestions = parser.get_suggestions()
        answer = builder.build_not_recognized(suggestions)
        assert "抱歉" in answer or "理解" in answer

    def test_all_tools_accessible(self):
        """测试所有工具可访问"""
        from services.query_executor import QueryExecutor
        executor = QueryExecutor()

        tools = executor.list_available_tools()
        expected_tools = [
            "count_projects",
            "list_ports",
            "list_containers",
            "system_status",
            "recent_errors",
            "get_project_summary",
            "scan_missing_readme",
            "recent_updates",
            "p0_health_check",
            "list_tmux",
        ]

        for tool_name in expected_tools:
            assert tool_name in tools, f"Missing tool: {tool_name}"

    def test_response_builder_all_templates(self):
        """测试所有响应模板"""
        from services.response_builder import ResponseBuilder
        builder = ResponseBuilder()

        # 测试数据
        test_cases = [
            ("count_projects", {"total": 100, "p0": 5, "p1": 20, "p2": 30, "p3": 45}),
            ("system_status", {"cpu": 45.0, "memory": 62.0, "disk": 71.0, "warning": "一切正常。"}),
            ("list_ports", {"count": 10, "ports": "80, 443, 3000"}),
        ]

        for intent, data in test_cases:
            answer = builder.build(intent, data)
            assert isinstance(answer, str)
            assert len(answer) > 0


class TestProjectIdNormalizer:
    """项目编号规范化测试"""

    def test_normalize_basic(self):
        from services.project_id_normalizer import normalize_project_id

        test_cases = [
            ("m536", "m536"),
            ("M536", "m536"),
            ("m 536", "m536"),
            ("m_536", "m536"),
        ]

        for input_id, expected in test_cases:
            result = normalize_project_id(input_id)
            assert result == expected, f"Failed for {input_id}: got {result}"

    def test_extract_from_text(self):
        from services.project_id_normalizer import extract_project_id_from_text

        test_cases = [
            ("m536是什么项目", "m536"),
            ("介绍一下m537", "m537"),
            ("项目520的情况", "m520"),
        ]

        for text, expected in test_cases:
            result = extract_project_id_from_text(text)
            assert result == expected, f"Failed for {text}: got {result}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
