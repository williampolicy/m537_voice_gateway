"""
M537 Voice Gateway - Intent Parser Tests
测试意图解析功能
"""
import pytest
import sys
import os

# 添加 backend 到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from services.intent_parser import IntentParser


class TestIntentParser:
    """意图解析器测试"""

    def setup_method(self):
        """每个测试前初始化"""
        self.parser = IntentParser()

    def test_count_projects_intent(self):
        """测试项目数量查询意图"""
        test_cases = [
            "现在有多少个项目",
            "项目总数是多少",
            "一共有几个项目",
            "有多少项目",
        ]
        for case in test_cases:
            intent, confidence, params = self.parser.parse(case)
            assert intent == "count_projects", f"Failed for: {case}"
            assert confidence >= 0.9

    def test_system_status_intent(self):
        """测试系统状态查询意图"""
        test_cases = [
            "系统状态怎么样",
            "CPU使用率",
            "内存占用多少",
        ]
        for case in test_cases:
            intent, confidence, params = self.parser.parse(case)
            assert intent == "system_status", f"Failed for: {case}"

    def test_disk_usage_intent(self):
        """测试磁盘使用情况查询意图"""
        test_cases = [
            "磁盘空间",
            "硬盘使用情况",
            "存储空间够吗",
        ]
        for case in test_cases:
            intent, confidence, params = self.parser.parse(case)
            assert intent == "disk_usage", f"Failed for: {case}"

    def test_list_ports_intent(self):
        """测试端口查询意图"""
        test_cases = [
            "当前有哪些端口在监听",
            "端口占用情况",
            "哪些端口开着",
        ]
        for case in test_cases:
            intent, confidence, params = self.parser.parse(case)
            assert intent == "list_ports", f"Failed for: {case}"

    def test_list_containers_intent(self):
        """测试容器查询意图"""
        test_cases = [
            "哪些Docker容器在运行",
            "容器状态",
            "运行中的容器",
        ]
        for case in test_cases:
            intent, confidence, params = self.parser.parse(case)
            assert intent == "list_containers", f"Failed for: {case}"

    def test_recent_errors_intent(self):
        """测试错误查询意图"""
        test_cases = [
            "最近有什么错误",
            "有没有报错",
            "异常日志",
        ]
        for case in test_cases:
            intent, confidence, params = self.parser.parse(case)
            assert intent == "recent_errors", f"Failed for: {case}"

    def test_project_summary_intent(self):
        """测试项目摘要查询意图"""
        test_cases = [
            ("m536是什么项目", "m536"),
            ("介绍一下m537", "m537"),
            ("什么是m520", "m520"),
        ]
        for transcript, expected_id in test_cases:
            intent, confidence, params = self.parser.parse(transcript)
            assert intent == "project_summary", f"Failed for: {transcript}"
            assert params.get("project_id") == expected_id

    def test_missing_readme_intent(self):
        """测试缺失 README 查询意图"""
        test_cases = [
            "哪些项目没有README",
            "缺少README的项目",
        ]
        for case in test_cases:
            intent, confidence, params = self.parser.parse(case)
            assert intent == "missing_readme", f"Failed for: {case}"

    def test_recent_updates_intent(self):
        """测试最近更新查询意图"""
        test_cases = [
            "最近更新了哪些项目",
            "近期有什么更新",
        ]
        for case in test_cases:
            intent, confidence, params = self.parser.parse(case)
            assert intent == "recent_updates", f"Failed for: {case}"

    def test_p0_health_intent(self):
        """测试 P0 服务状态查询意图"""
        test_cases = [
            "P0服务状态如何",
            "关键服务状态",
        ]
        for case in test_cases:
            intent, confidence, params = self.parser.parse(case)
            assert intent == "p0_health", f"Failed for: {case}"

    def test_list_tmux_intent(self):
        """测试 tmux 会话查询意图"""
        test_cases = [
            "当前有哪些tmux session",
            "tmux会话列表",
        ]
        for case in test_cases:
            intent, confidence, params = self.parser.parse(case)
            assert intent == "list_tmux", f"Failed for: {case}"

    def test_unknown_intent(self):
        """测试无法识别的意图"""
        test_cases = [
            "今天天气怎么样",
            "你叫什么名字",
            "1加1等于几",
        ]
        for case in test_cases:
            intent, confidence, params = self.parser.parse(case)
            assert intent is None, f"Should not match: {case}"
            assert confidence == 0.0

    def test_get_suggestions(self):
        """测试获取建议"""
        suggestions = self.parser.get_suggestions()
        assert len(suggestions) > 0
        assert all(isinstance(s, str) for s in suggestions)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
