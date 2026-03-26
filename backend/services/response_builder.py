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
        "count_projects": {
            "success": "当前共有 {total} 个项目，其中 P0 项目 {p0} 个，P1 项目 {p1} 个，P2 项目 {p2} 个，P3 项目 {p3} 个。",
            "empty": "当前没有任何项目。"
        },
        "list_ports": {
            "success": "当前共有 {count} 个端口在监听：{ports}",
            "empty": "当前没有端口在监听。"
        },
        "list_containers": {
            "success": "当前有 {running} 个容器在运行，{stopped} 个已停止。运行中的容器包括：{names}",
            "empty": "当前没有 Docker 容器。"
        },
        "system_status": {
            "success": "系统状态：CPU 使用率 {cpu}%，内存使用率 {memory}%，磁盘使用率 {disk}%。{warning}",
        },
        "recent_errors": {
            "success": "最近 24 小时发现 {count} 个错误：{errors}",
            "empty": "最近 24 小时没有发现错误，一切正常！"
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
        "p0_health": {
            "all_healthy": "所有 P0 关键服务状态正常！共 {count} 个服务在运行。",
            "has_issues": "注意！有 {unhealthy} 个 P0 服务异常：{services}"
        },
        "list_tmux": {
            "success": "当前有 {count} 个 tmux session：{sessions}",
            "empty": "当前没有 tmux session。"
        },
        "not_recognized": {
            "default": "抱歉，我没有理解你的问题。你可以尝试问：{suggestions}"
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

        templates = self.TEMPLATES.get(intent, {})

        # Select appropriate template based on data
        template = self._select_template(templates, data)

        try:
            # Ensure all required fields have defaults
            data_with_defaults = self._add_defaults(data, intent)
            return template.format(**data_with_defaults)
        except KeyError as e:
            return f"数据格式错误，缺少字段: {e}"
        except Exception as e:
            return f"响应构建错误: {e}"

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
