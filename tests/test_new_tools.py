"""
M537 Voice Gateway - New Tools Tests
测试新增的7个语音查询工具
"""
import pytest
import sys
import os

# 添加 backend 到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from tools.disk_usage import DiskUsageTool
from tools.uptime_info import UptimeInfoTool
from tools.process_list import ProcessListTool
from tools.network_info import NetworkInfoTool
from tools.git_status import GitStatusTool
from tools.service_logs import ServiceLogsTool
from tools.cron_jobs import CronJobsTool


class TestDiskUsageTool:
    """磁盘使用情况工具测试"""

    def setup_method(self):
        self.tool = DiskUsageTool()

    def test_execute_returns_success(self):
        """测试执行返回成功"""
        result = self.tool.execute({})
        assert result.get("success") is True

    def test_execute_has_partitions(self):
        """测试返回分区信息"""
        result = self.tool.execute({})
        assert "partitions" in result
        assert isinstance(result["partitions"], list)

    def test_execute_has_partition_count(self):
        """测试返回分区数量"""
        result = self.tool.execute({})
        assert "partition_count" in result
        assert result["partition_count"] >= 0

    def test_partition_has_required_fields(self):
        """测试分区包含必要字段"""
        result = self.tool.execute({})
        if result["partitions"]:
            partition = result["partitions"][0]
            assert "filesystem" in partition
            assert "size" in partition
            assert "used" in partition
            assert "use_percent" in partition


class TestUptimeInfoTool:
    """系统运行时间工具测试"""

    def setup_method(self):
        self.tool = UptimeInfoTool()

    def test_execute_returns_success(self):
        """测试执行返回成功"""
        result = self.tool.execute({})
        assert result.get("success") is True

    def test_execute_has_uptime(self):
        """测试返回运行时间"""
        result = self.tool.execute({})
        assert "uptime" in result
        uptime = result["uptime"]
        assert "days" in uptime
        assert "hours" in uptime
        assert "human_readable" in uptime

    def test_execute_has_load_average(self):
        """测试返回负载信息"""
        result = self.tool.execute({})
        assert "load_average" in result
        load = result["load_average"]
        assert "1min" in load
        assert "5min" in load
        assert "15min" in load
        assert "status" in load

    def test_execute_has_cpu_count(self):
        """测试返回CPU核心数"""
        result = self.tool.execute({})
        assert "cpu_count" in result
        assert result["cpu_count"] > 0


class TestProcessListTool:
    """进程列表工具测试"""

    def setup_method(self):
        self.tool = ProcessListTool()

    def test_execute_returns_success(self):
        """测试执行返回成功"""
        result = self.tool.execute({})
        assert result.get("success") is True

    def test_execute_has_total_processes(self):
        """测试返回进程总数"""
        result = self.tool.execute({})
        assert "total_processes" in result
        assert result["total_processes"] > 0

    def test_execute_has_top_cpu(self):
        """测试返回CPU占用排行"""
        result = self.tool.execute({})
        assert "top_cpu" in result
        assert isinstance(result["top_cpu"], list)

    def test_execute_has_top_memory(self):
        """测试返回内存占用排行"""
        result = self.tool.execute({})
        assert "top_memory" in result
        assert isinstance(result["top_memory"], list)

    def test_process_has_required_fields(self):
        """测试进程信息包含必要字段"""
        result = self.tool.execute({})
        if result["top_cpu"]:
            process = result["top_cpu"][0]
            assert "pid" in process
            assert "cpu" in process
            assert "command" in process


class TestNetworkInfoTool:
    """网络信息工具测试"""

    def setup_method(self):
        self.tool = NetworkInfoTool()

    def test_execute_returns_success(self):
        """测试执行返回成功"""
        result = self.tool.execute({})
        assert result.get("success") is True

    def test_execute_has_connections(self):
        """测试返回连接信息"""
        result = self.tool.execute({})
        assert "connections" in result
        connections = result["connections"]
        assert "established" in connections
        assert "listen" in connections

    def test_execute_has_interfaces(self):
        """测试返回网卡信息"""
        result = self.tool.execute({})
        assert "interfaces" in result
        assert isinstance(result["interfaces"], list)

    def test_execute_has_total_connections(self):
        """测试返回总连接数"""
        result = self.tool.execute({})
        assert "total_connections" in result


class TestGitStatusTool:
    """Git状态工具测试"""

    def setup_method(self):
        self.tool = GitStatusTool()

    def test_execute_summary_mode(self):
        """测试汇总模式"""
        result = self.tool.execute({})
        assert result.get("success") is True
        assert "total_projects" in result
        assert "git_repos" in result

    def test_execute_with_valid_project(self):
        """测试有效项目"""
        result = self.tool.execute({"project_id": "m537"})
        assert result.get("success") is True
        # 可能是git仓库或不是
        assert "is_git_repo" in result or "total_projects" in result

    def test_execute_with_invalid_project(self):
        """测试无效项目"""
        result = self.tool.execute({"project_id": "nonexistent_xyz_123"})
        # 应该返回错误或空结果
        assert "success" in result


class TestServiceLogsTool:
    """服务日志工具测试"""

    def setup_method(self):
        self.tool = ServiceLogsTool()

    def test_execute_returns_success(self):
        """测试执行返回成功"""
        result = self.tool.execute({})
        assert result.get("success") is True

    def test_execute_has_log_entries(self):
        """测试返回日志条目"""
        result = self.tool.execute({})
        assert "log_entries" in result
        assert isinstance(result["log_entries"], list)

    def test_execute_has_timestamp(self):
        """测试返回时间戳"""
        result = self.tool.execute({})
        assert "timestamp" in result


class TestCronJobsTool:
    """定时任务工具测试"""

    def setup_method(self):
        self.tool = CronJobsTool()

    def test_execute_returns_success(self):
        """测试执行返回成功"""
        result = self.tool.execute({})
        assert result.get("success") is True

    def test_execute_has_jobs(self):
        """测试返回任务列表"""
        result = self.tool.execute({})
        assert "jobs" in result
        assert isinstance(result["jobs"], list)

    def test_execute_has_total_count(self):
        """测试返回任务总数"""
        result = self.tool.execute({})
        assert "total_count" in result


class TestNewIntents:
    """新意图解析测试"""

    def setup_method(self):
        from services.intent_parser import IntentParser
        self.parser = IntentParser()

    def test_uptime_intent(self):
        """测试运行时间意图"""
        test_cases = [
            "系统运行时间",
            "开机多久了",
            "uptime",
        ]
        for case in test_cases:
            intent, confidence, params = self.parser.parse(case)
            assert intent == "uptime_info", f"Failed for: {case}"

    def test_process_intent(self):
        """测试进程意图"""
        test_cases = [
            "有哪些进程",
            "运行的程序",
            "进程列表",
        ]
        for case in test_cases:
            intent, confidence, params = self.parser.parse(case)
            assert intent == "process_list", f"Failed for: {case}"

    def test_network_intent(self):
        """测试网络意图"""
        test_cases = [
            "网络状态",
            "ip地址",
            "网络连接",
        ]
        for case in test_cases:
            intent, confidence, params = self.parser.parse(case)
            assert intent == "network_info", f"Failed for: {case}"

    def test_git_intent(self):
        """测试Git意图"""
        test_cases = [
            "git状态",
            "代码状态",
            "仓库状态",
        ]
        for case in test_cases:
            intent, confidence, params = self.parser.parse(case)
            assert intent == "git_status", f"Failed for: {case}"

    def test_logs_intent(self):
        """测试日志意图"""
        test_cases = [
            "查看日志",
            "服务日志",
            "系统日志",
        ]
        for case in test_cases:
            intent, confidence, params = self.parser.parse(case)
            assert intent == "service_logs", f"Failed for: {case}"

    def test_cron_intent(self):
        """测试定时任务意图"""
        test_cases = [
            "定时任务",
            "cron",
            "计划任务",
        ]
        for case in test_cases:
            intent, confidence, params = self.parser.parse(case)
            assert intent == "cron_jobs", f"Failed for: {case}"
