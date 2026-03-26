"""
M537 Voice Gateway - Tools Tests
测试白名单工具
"""
import pytest
import sys
import os

# 添加 backend 到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))


class TestCountProjectsTool:
    """项目统计工具测试"""

    def test_execute(self):
        from tools.count_projects import CountProjectsTool
        tool = CountProjectsTool()
        result = tool.execute({})

        assert "total" in result
        assert "p0" in result
        assert "p1" in result
        assert "p2" in result
        assert "p3" in result
        assert isinstance(result["total"], int)
        assert result["total"] >= 0


class TestSystemStatusTool:
    """系统状态工具测试"""

    def test_execute(self):
        from tools.system_status import SystemStatusTool
        tool = SystemStatusTool()
        result = tool.execute({})

        assert "cpu" in result
        assert "memory" in result
        assert "disk" in result
        assert "warning" in result
        assert 0 <= result["cpu"] <= 100
        assert 0 <= result["memory"] <= 100
        assert 0 <= result["disk"] <= 100


class TestListPortsTool:
    """端口列表工具测试"""

    def test_execute(self):
        from tools.list_ports import ListPortsTool
        tool = ListPortsTool()
        result = tool.execute({})

        assert "count" in result
        assert "ports" in result
        assert isinstance(result["count"], int)


class TestGetProjectSummaryTool:
    """项目摘要工具测试"""

    def test_execute_with_valid_project(self):
        from tools.get_project_summary import GetProjectSummaryTool
        tool = GetProjectSummaryTool()
        result = tool.execute({"project_id": "m537"})

        assert "project_id" in result
        assert "title" in result or "not_found" in result

    def test_execute_with_invalid_project(self):
        from tools.get_project_summary import GetProjectSummaryTool
        tool = GetProjectSummaryTool()
        result = tool.execute({"project_id": "m99999"})

        assert result.get("not_found") == True

    def test_execute_without_project_id(self):
        from tools.get_project_summary import GetProjectSummaryTool
        tool = GetProjectSummaryTool()
        result = tool.execute({})

        assert result.get("not_found") == True


class TestScanMissingReadmeTool:
    """扫描缺失 README 工具测试"""

    def test_execute(self):
        from tools.scan_missing_readme import ScanMissingReadmeTool
        tool = ScanMissingReadmeTool()
        result = tool.execute({})

        assert "count" in result
        assert "projects" in result
        assert isinstance(result["count"], int)


class TestRecentUpdatesTool:
    """最近更新工具测试"""

    def test_execute(self):
        from tools.recent_updates import RecentUpdatesTool
        tool = RecentUpdatesTool()
        result = tool.execute({})

        assert "count" in result
        assert "projects" in result
        assert "days" in result
        assert isinstance(result["count"], int)

    def test_execute_with_custom_days(self):
        from tools.recent_updates import RecentUpdatesTool
        tool = RecentUpdatesTool()
        result = tool.execute({"days": 3})

        assert result["days"] == 3


class TestP0HealthCheckTool:
    """P0 健康检查工具测试"""

    def test_execute(self):
        from tools.p0_health_check import P0HealthCheckTool
        tool = P0HealthCheckTool()
        result = tool.execute({})

        assert "healthy" in result or "all_healthy" in result or "count" in result


class TestListTmuxTool:
    """Tmux 列表工具测试"""

    def test_execute(self):
        from tools.list_tmux import ListTmuxTool
        tool = ListTmuxTool()
        result = tool.execute({})

        assert "count" in result
        assert "sessions" in result


class TestListContainersTool:
    """容器列表工具测试"""

    def test_execute(self):
        from tools.list_containers import ListContainersTool
        tool = ListContainersTool()
        result = tool.execute({})

        # 可能返回错误（Docker 权限问题）或正常结果
        assert "running" in result or "error" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
