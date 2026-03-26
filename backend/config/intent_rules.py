"""
M537 Voice Gateway - Intent Rules Configuration
Rule-based intent matching for voice queries
"""

INTENT_RULES = {
    "count_projects": {
        "keywords": [
            "多少个项目", "项目数", "几个项目", "项目总数",
            "有多少项目", "项目数量", "一共有多少", "总共有多少"
        ],
        "tool": "count_projects",
        "description": "统计项目总数"
    },
    "list_ports": {
        "keywords": [
            "端口", "哪些端口", "端口监听", "开放端口",
            "端口开着", "监听端口", "端口状态"
        ],
        "tool": "list_ports",
        "description": "列出监听端口"
    },
    "list_containers": {
        "keywords": [
            "容器", "docker", "哪些容器", "容器在运行",
            "运行的容器", "docker容器", "容器状态"
        ],
        "tool": "list_containers",
        "description": "列出运行中的容器"
    },
    "system_status": {
        "keywords": [
            "cpu", "内存", "磁盘", "系统状态", "资源",
            "状态怎么样", "系统资源", "负载", "使用率"
        ],
        "tool": "system_status",
        "description": "查询系统资源状态"
    },
    "recent_errors": {
        "keywords": [
            "错误", "报错", "异常", "出错", "error",
            "有什么错", "最近的错误", "错误日志"
        ],
        "tool": "recent_errors",
        "description": "查询最近错误"
    },
    "project_summary": {
        "keywords": [
            "是什么项目", "项目介绍", "项目简介", "什么是",
            "是什么", "是啥", "介绍一下"
        ],
        "tool": "get_project_summary",
        "params": ["project_id"],
        "description": "获取项目摘要"
    },
    "missing_readme": {
        "keywords": [
            "没有readme", "缺少readme", "readme缺失",
            "哪些项目没有", "缺失的readme"
        ],
        "tool": "scan_missing_readme",
        "description": "扫描缺失README的项目"
    },
    "recent_updates": {
        "keywords": [
            "最近更新", "近期更新", "更新了", "最新改动",
            "最近修改", "近期修改", "有什么更新"
        ],
        "tool": "recent_updates",
        "params": ["days"],
        "description": "查询最近更新的项目"
    },
    "p0_health": {
        "keywords": [
            "p0", "关键服务", "核心服务", "重要服务",
            "p0状态", "p0服务"
        ],
        "tool": "p0_health_check",
        "description": "检查P0服务状态"
    },
    "list_tmux": {
        "keywords": [
            "tmux", "session", "会话", "tmux会话",
            "tmux session"
        ],
        "tool": "list_tmux",
        "description": "列出tmux会话"
    }
}
