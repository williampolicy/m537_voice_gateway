"""
M537 Voice Gateway - Response Builder Service
Builds natural language responses from data
"""
from typing import Dict, Any, List


class ResponseBuilder:
    """
    Response builder that converts structured data to natural language.
    """

    TEMPLATES = {
        # ========== 项目相关 ==========
        "count_projects": {
            "success": "当前共有 {total} 个项目，其中 P0 项目 {p0} 个，P1 项目 {p1} 个，P2 项目 {p2} 个，P3 项目 {p3} 个。",
            "empty": "当前没有任何项目。"
        },
        "project_summary": {
            "success": "项目 {project_id}：{title}。{description}",
            "not_found": "没有找到项目 {project_id}。"
        },
        "missing_readme": {
            "success": "共有 {count} 个项目缺少 README：{projects}",
            "empty": "所有项目都有 README，很棒！"
        },
        "recent_updates": {
            "success": "最近 {days} 天有 {count} 个项目更新：{projects}",
            "empty": "最近 {days} 天没有项目更新。"
        },
        "git_status": {
            "success": "项目 {project_id} 的 Git 状态：分支 {branch}，{modified_count} 个文件已修改，{untracked_count} 个未跟踪文件。{last_commit_info}",
            "clean": "项目 {project_id} 的 Git 仓库状态干净，没有待提交的更改。当前分支：{branch}",
            "summary": "共扫描 {total_projects} 个项目，其中 {git_repos} 个是 Git 仓库，{clean_repos} 个状态干净，{dirty_count} 个有待提交的更改。",
            "not_git": "项目 {project_id} 不是 Git 仓库。"
        },

        # ========== 系统相关 ==========
        "system_status": {
            "success": "系统状态：CPU 使用率 {cpu}%，内存使用率 {memory}%，磁盘使用率 {disk}%。{warning}",
        },
        "disk_usage": {
            "success": "磁盘使用情况：共 {partition_count} 个分区。{partition_info}总容量 {total_size}，已使用 {total_used}，可用 {total_available}。",
            "empty": "无法获取磁盘信息。"
        },
        "uptime_info": {
            "success": "系统已运行 {uptime}。负载状态：{load_status}（1分钟负载 {load_1}，5分钟负载 {load_5}，15分钟负载 {load_15}）。{cpu_count} 核心，{logged_in_users} 个用户在线。",
        },
        "process_list": {
            "success": "当前共有 {total_processes} 个进程运行。CPU 占用最高：{top_cpu_info}。内存占用最高：{top_mem_info}。",
            "with_zombie": "当前共有 {total_processes} 个进程，其中 {zombie_processes} 个僵尸进程需要关注。"
        },

        # ========== 网络相关 ==========
        "list_ports": {
            "success": "当前共有 {count} 个端口在监听：{ports}",
            "empty": "当前没有端口在监听。"
        },
        "network_info": {
            "success": "网络状态：{established} 个已建立连接，{listen} 个监听端口。{interface_info}{public_ip_info}",
        },

        # ========== 容器和服务 ==========
        "list_containers": {
            "success": "当前有 {running} 个容器在运行，{stopped} 个已停止。运行中的容器包括：{names}",
            "empty": "当前没有 Docker 容器。"
        },
        "p0_health": {
            "all_healthy": "所有 P0 关键服务状态正常！共 {count} 个服务在运行。",
            "has_issues": "注意！有 {unhealthy} 个 P0 服务异常：{services}"
        },
        "list_tmux": {
            "success": "当前有 {count} 个 tmux session：{sessions}",
            "empty": "当前没有 tmux session。"
        },

        # ========== 日志和错误 ==========
        "recent_errors": {
            "success": "最近 24 小时发现 {count} 个错误：{errors}",
            "empty": "最近 24 小时没有发现错误，一切正常！"
        },
        "service_logs": {
            "success": "获取到 {total_entries} 条日志记录：{log_summary}",
            "empty": "没有找到相关日志。"
        },

        # ========== 定时任务 ==========
        "cron_jobs": {
            "success": "共有 {total_count} 个定时任务：{job_summary}",
            "empty": "当前没有配置定时任务。"
        },

        # ========== 错误处理 ==========
        "not_recognized": {
            "default": "抱歉，我没有理解你的问题。你可以尝试问：{suggestions}"
        },
        "error": {
            "execution_failed": "执行查询时遇到问题：{error}。请稍后重试。",
            "timeout": "查询超时，服务器繁忙。请稍后重试。",
            "permission": "没有权限执行此操作。",
            "not_found": "没有找到相关信息。"
        }
    }

    def build(self, intent: str, data: Dict[str, Any], success: bool = True) -> str:
        """
        Build natural language response from data.

        Args:
            intent: The identified intent
            data: Data from tool execution
            success: Whether the execution was successful

        Returns:
            Natural language response string
        """
        if not success:
            return f"查询失败：{data.get('error', '未知错误')}"

        # Handle nested success data
        if isinstance(data, dict) and "success" in data:
            if not data.get("success"):
                return f"查询失败：{data.get('error', '未知错误')}"
            # Use the data directly, it may contain the actual response fields
            actual_data = data
        else:
            actual_data = data

        templates = self.TEMPLATES.get(intent, {})

        # Special handlers for new tools
        if intent == "git_status":
            return self._build_git_status(actual_data, templates)
        elif intent == "disk_usage":
            return self._build_disk_usage(actual_data, templates)
        elif intent == "uptime_info":
            return self._build_uptime_info(actual_data, templates)
        elif intent == "process_list":
            return self._build_process_list(actual_data, templates)
        elif intent == "network_info":
            return self._build_network_info(actual_data, templates)
        elif intent == "service_logs":
            return self._build_service_logs(actual_data, templates)
        elif intent == "cron_jobs":
            return self._build_cron_jobs(actual_data, templates)

        # Select appropriate template based on data
        template = self._select_template(templates, actual_data)

        try:
            # Ensure all required fields have defaults
            data_with_defaults = self._add_defaults(actual_data, intent)
            return template.format(**data_with_defaults)
        except KeyError as e:
            return f"数据格式错误，缺少字段: {e}"
        except Exception as e:
            return f"响应构建错误: {e}"

    def _build_git_status(self, data: Dict[str, Any], templates: Dict[str, str]) -> str:
        """Build response for git_status"""
        if data.get("is_git_repo") is False:
            return templates.get("not_git", "").format(**data)

        if "total_projects" in data:
            # Summary mode
            dirty_count = len(data.get("dirty_repos", []))
            return templates.get("summary", "").format(
                total_projects=data.get("total_projects", 0),
                git_repos=data.get("git_repos", 0),
                clean_repos=data.get("clean_repos", 0),
                dirty_count=dirty_count
            )

        # Single project mode
        if data.get("is_clean"):
            return templates.get("clean", "").format(
                project_id=data.get("project_id", ""),
                branch=data.get("branch", "main")
            )

        last_commit = data.get("last_commit", {})
        last_commit_info = ""
        if last_commit:
            last_commit_info = f"最近提交：{last_commit.get('message', '')} ({last_commit.get('relative_time', '')})"

        return templates.get("success", "").format(
            project_id=data.get("project_id", ""),
            branch=data.get("branch", "main"),
            modified_count=data.get("modified_count", 0),
            untracked_count=data.get("untracked_count", 0),
            last_commit_info=last_commit_info
        )

    def _build_disk_usage(self, data: Dict[str, Any], templates: Dict[str, str]) -> str:
        """Build response for disk_usage"""
        partitions = data.get("partitions", [])
        total = data.get("total", {})

        if not partitions:
            return templates.get("empty", "无法获取磁盘信息。")

        partition_info = ""
        for p in partitions[:3]:
            partition_info += f"{p.get('mounted_on', '/')} 使用 {p.get('use_percent', '0%')}；"

        return templates.get("success", "").format(
            partition_count=len(partitions),
            partition_info=partition_info,
            total_size=total.get("size", "未知") if total else "未知",
            total_used=total.get("used", "未知") if total else "未知",
            total_available=total.get("available", "未知") if total else "未知"
        )

    def _build_uptime_info(self, data: Dict[str, Any], templates: Dict[str, str]) -> str:
        """Build response for uptime_info"""
        uptime = data.get("uptime", {})
        load = data.get("load_average", {})

        return templates.get("success", "").format(
            uptime=uptime.get("human_readable", "未知"),
            load_status=load.get("status", "未知"),
            load_1=load.get("1min", 0),
            load_5=load.get("5min", 0),
            load_15=load.get("15min", 0),
            cpu_count=data.get("cpu_count", 0),
            logged_in_users=data.get("logged_in_users", 0)
        )

    def _build_process_list(self, data: Dict[str, Any], templates: Dict[str, str]) -> str:
        """Build response for process_list"""
        top_cpu = data.get("top_cpu", [])
        top_mem = data.get("top_memory", [])

        top_cpu_info = "、".join([f"{p.get('command', '')[:20]}({p.get('cpu', 0)}%)" for p in top_cpu[:3]])
        top_mem_info = "、".join([f"{p.get('command', '')[:20]}({p.get('mem', 0)}%)" for p in top_mem[:3]])

        zombie = data.get("zombie_processes", 0)
        if zombie > 0:
            return templates.get("with_zombie", "").format(
                total_processes=data.get("total_processes", 0),
                zombie_processes=zombie
            )

        return templates.get("success", "").format(
            total_processes=data.get("total_processes", 0),
            top_cpu_info=top_cpu_info or "无",
            top_mem_info=top_mem_info or "无"
        )

    def _build_network_info(self, data: Dict[str, Any], templates: Dict[str, str]) -> str:
        """Build response for network_info"""
        connections = data.get("connections", {})
        interfaces = data.get("interfaces", [])
        public_ip = data.get("public_ip")

        interface_info = ""
        for iface in interfaces[:2]:
            interface_info += f"{iface.get('interface', '')}={iface.get('address', '')}；"

        public_ip_info = f"公网IP：{public_ip}" if public_ip else ""

        return templates.get("success", "").format(
            established=connections.get("established", 0),
            listen=connections.get("listen", 0),
            interface_info=interface_info,
            public_ip_info=public_ip_info
        )

    def _build_service_logs(self, data: Dict[str, Any], templates: Dict[str, str]) -> str:
        """Build response for service_logs"""
        entries = data.get("log_entries", [])

        if not entries:
            return templates.get("empty", "没有找到相关日志。")

        log_summary = "、".join([f"{e.get('source', '')}:{e.get('message', '')[:30]}" for e in entries[:3]])

        return templates.get("success", "").format(
            total_entries=data.get("total_entries", 0),
            log_summary=log_summary
        )

    def _build_cron_jobs(self, data: Dict[str, Any], templates: Dict[str, str]) -> str:
        """Build response for cron_jobs"""
        jobs = data.get("jobs", [])

        if not jobs:
            return templates.get("empty", "当前没有配置定时任务。")

        job_summary = "、".join([f"{j.get('schedule', '')}执行{j.get('command', '')[:20]}" for j in jobs[:5]])

        return templates.get("success", "").format(
            total_count=data.get("total_count", 0),
            job_summary=job_summary
        )

    def _select_template(self, templates: Dict[str, str], data: Dict[str, Any]) -> str:
        """Select the appropriate template based on data"""
        if not data:
            return templates.get("empty", templates.get("success", ""))

        # Check for specific conditions
        if data.get("not_found"):
            return templates.get("not_found", templates.get("success", ""))

        if data.get("total", 1) == 0 or data.get("count", 1) == 0:
            return templates.get("empty", templates.get("success", ""))

        if data.get("unhealthy", 0) > 0:
            return templates.get("has_issues", templates.get("success", ""))

        if data.get("all_healthy"):
            return templates.get("all_healthy", templates.get("success", ""))

        return templates.get("success", "")

    def _add_defaults(self, data: Dict[str, Any], intent: str) -> Dict[str, Any]:
        """Add default values for missing fields"""
        result = dict(data)

        # Common defaults
        defaults = {
            "total": 0,
            "count": 0,
            "p0": 0,
            "p1": 0,
            "p2": 0,
            "p3": 0,
            "running": 0,
            "stopped": 0,
            "unhealthy": 0,
            "days": 7,
            "ports": "",
            "names": "",
            "errors": "",
            "projects": "",
            "sessions": "",
            "services": "",
            "warning": "",
            "title": "",
            "description": "",
            "project_id": "",
            "cpu": 0,
            "memory": 0,
            "disk": 0
        }

        for key, default_value in defaults.items():
            if key not in result:
                result[key] = default_value

        return result

    def build_not_recognized(self, suggestions: List[str]) -> str:
        """Build response for unrecognized intent"""
        template = self.TEMPLATES["not_recognized"]["default"]
        return template.format(suggestions="、".join(suggestions[:3]))

    def build_error(self, error_type: str, error_message: str = "") -> str:
        """Build error response"""
        templates = self.TEMPLATES.get("error", {})
        template = templates.get(error_type, templates.get("execution_failed", "发生错误：{error}"))
        return template.format(error=error_message)
