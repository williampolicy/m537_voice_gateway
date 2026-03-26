"""
M537 Voice Gateway - Tool Registry
Registry of available whitelist tools
"""

TOOL_REGISTRY = {
    # ========== 项目相关 ==========
    "count_projects": {
        "module": "count_projects",
        "class": "CountProjectsTool",
        "description": "统计项目数量"
    },
    "project_summary": {
        "module": "get_project_summary",
        "class": "GetProjectSummaryTool",
        "description": "获取项目摘要"
    },
    "missing_readme": {
        "module": "scan_missing_readme",
        "class": "ScanMissingReadmeTool",
        "description": "扫描缺失README"
    },
    "recent_updates": {
        "module": "recent_updates",
        "class": "RecentUpdatesTool",
        "description": "查询最近更新"
    },
    "git_status": {
        "module": "git_status",
        "class": "GitStatusTool",
        "description": "查询Git仓库状态"
    },

    # ========== 系统相关 ==========
    "system_status": {
        "module": "system_status",
        "class": "SystemStatusTool",
        "description": "查询系统状态"
    },
    "disk_usage": {
        "module": "disk_usage",
        "class": "DiskUsageTool",
        "description": "查询磁盘使用情况"
    },
    "uptime_info": {
        "module": "uptime_info",
        "class": "UptimeInfoTool",
        "description": "查询系统运行时间"
    },
    "process_list": {
        "module": "process_list",
        "class": "ProcessListTool",
        "description": "查询运行中的进程"
    },

    # ========== 网络相关 ==========
    "list_ports": {
        "module": "list_ports",
        "class": "ListPortsTool",
        "description": "列出监听端口"
    },
    "network_info": {
        "module": "network_info",
        "class": "NetworkInfoTool",
        "description": "查询网络信息"
    },

    # ========== 容器和服务 ==========
    "list_containers": {
        "module": "list_containers",
        "class": "ListContainersTool",
        "description": "列出Docker容器"
    },
    "p0_health": {
        "module": "p0_health_check",
        "class": "P0HealthCheckTool",
        "description": "检查P0服务状态"
    },
    "list_tmux": {
        "module": "list_tmux",
        "class": "ListTmuxTool",
        "description": "列出tmux会话"
    },

    # ========== 日志和错误 ==========
    "recent_errors": {
        "module": "recent_errors",
        "class": "RecentErrorsTool",
        "description": "查询最近错误"
    },
    "service_logs": {
        "module": "service_logs",
        "class": "ServiceLogsTool",
        "description": "查询服务日志"
    },

    # ========== 定时任务 ==========
    "cron_jobs": {
        "module": "cron_jobs",
        "class": "CronJobsTool",
        "description": "列出定时任务"
    }
}

# Tool count for metrics
TOTAL_TOOLS = len(TOOL_REGISTRY)
