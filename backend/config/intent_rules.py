"""
M537 Voice Gateway - Intent Rules Configuration
Rule-based intent matching for voice queries
"""

INTENT_RULES = {
    # ========== 项目相关 ==========
    "count_projects": {
        "keywords": [
            "多少个项目", "项目数", "几个项目", "项目总数",
            "有多少项目", "项目数量", "一共有多少", "总共有多少"
        ],
        "tool": "count_projects",
        "description": "统计项目总数"
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
    "git_status": {
        "keywords": [
            "git状态", "git", "代码状态", "提交状态",
            "仓库状态", "有没有提交", "代码改动"
        ],
        "tool": "git_status",
        "params": ["project_id"],
        "description": "查询Git仓库状态"
    },

    # ========== 系统相关 ==========
    "system_status": {
        "keywords": [
            "cpu", "内存", "系统状态", "资源",
            "状态怎么样", "系统资源", "负载", "使用率"
        ],
        "tool": "system_status",
        "description": "查询系统资源状态"
    },
    "disk_usage": {
        "keywords": [
            "磁盘", "硬盘", "存储", "空间",
            "磁盘使用", "磁盘空间", "存储空间", "硬盘空间"
        ],
        "tool": "disk_usage",
        "description": "查询磁盘使用情况"
    },
    "uptime_info": {
        "keywords": [
            "运行时间", "启动时间", "开机多久", "uptime",
            "运行了多久", "系统启动", "开机时间"
        ],
        "tool": "uptime_info",
        "description": "查询系统运行时间"
    },
    "process_list": {
        "keywords": [
            "进程", "运行的程序", "哪些程序", "进程列表",
            "什么在运行", "跑着什么"
        ],
        "tool": "process_list",
        "description": "查询运行中的进程"
    },

    # ========== 网络相关 ==========
    "list_ports": {
        "keywords": [
            "端口", "哪些端口", "端口监听", "开放端口",
            "端口开着", "监听端口", "端口状态"
        ],
        "tool": "list_ports",
        "description": "列出监听端口"
    },
    "network_info": {
        "keywords": [
            "网络", "连接", "ip地址", "网卡",
            "网络状态", "网络连接", "ip"
        ],
        "tool": "network_info",
        "description": "查询网络信息"
    },

    # ========== 容器和服务 ==========
    "list_containers": {
        "keywords": [
            "容器", "docker", "哪些容器", "容器在运行",
            "运行的容器", "docker容器", "容器状态"
        ],
        "tool": "list_containers",
        "description": "列出运行中的容器"
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
    },

    # ========== 日志和错误 ==========
    "recent_errors": {
        "keywords": [
            "错误", "报错", "异常", "出错", "error",
            "有什么错", "最近的错误", "错误日志"
        ],
        "tool": "recent_errors",
        "description": "查询最近错误"
    },
    "service_logs": {
        "keywords": [
            "日志", "log", "logs", "查看日志",
            "服务日志", "系统日志"
        ],
        "tool": "service_logs",
        "params": ["service", "lines"],
        "description": "查询服务日志"
    },

    # ========== 定时任务 ==========
    "cron_jobs": {
        "keywords": [
            "定时任务", "cron", "计划任务", "自动任务",
            "定时", "周期任务", "调度任务"
        ],
        "tool": "cron_jobs",
        "description": "列出定时任务"
    }
}

# Intent categories for organization
INTENT_CATEGORIES = {
    "项目管理": ["count_projects", "project_summary", "missing_readme", "recent_updates", "git_status"],
    "系统监控": ["system_status", "disk_usage", "uptime_info", "process_list"],
    "网络状态": ["list_ports", "network_info"],
    "容器服务": ["list_containers", "p0_health", "list_tmux"],
    "日志分析": ["recent_errors", "service_logs"],
    "任务调度": ["cron_jobs"]
}

# Intent count for metrics
TOTAL_INTENTS = len(INTENT_RULES)
