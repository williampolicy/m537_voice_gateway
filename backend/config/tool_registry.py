"""
M537 Voice Gateway - Tool Registry
Registry of available whitelist tools
"""

TOOL_REGISTRY = {
    "count_projects": {
        "module": "count_projects",
        "class": "CountProjectsTool",
        "description": "统计项目数量"
    },
    "list_ports": {
        "module": "list_ports",
        "class": "ListPortsTool",
        "description": "列出监听端口"
    },
    "list_containers": {
        "module": "list_containers",
        "class": "ListContainersTool",
        "description": "列出Docker容器"
    },
    "system_status": {
        "module": "system_status",
        "class": "SystemStatusTool",
        "description": "查询系统状态"
    },
    "recent_errors": {
        "module": "recent_errors",
        "class": "RecentErrorsTool",
        "description": "查询最近错误"
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
    "p0_health": {
        "module": "p0_health_check",
        "class": "P0HealthCheckTool",
        "description": "检查P0服务状态"
    },
    "list_tmux": {
        "module": "list_tmux",
        "class": "ListTmuxTool",
        "description": "列出tmux会话"
    }
}
