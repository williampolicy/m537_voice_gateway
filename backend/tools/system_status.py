"""
M537 Voice Gateway - System Status Tool
Queries system resource usage
"""
import psutil
from typing import Dict, Any

from tools.base_tool import BaseTool


class SystemStatusTool(BaseTool):
    """Query system resource status"""

    name = "system_status"
    description = "查询 CPU、内存、磁盘使用率"

    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        cpu = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory().percent
        disk = psutil.disk_usage("/").percent

        # Generate warning messages
        warnings = []
        if cpu > 80:
            warnings.append("CPU 使用率过高")
        if memory > 80:
            warnings.append("内存使用率过高")
        if disk > 90:
            warnings.append("磁盘空间不足")

        warning_text = "注意：" + "，".join(warnings) if warnings else "一切正常。"

        return {
            "cpu": round(cpu, 1),
            "memory": round(memory, 1),
            "disk": round(disk, 1),
            "warning": warning_text
        }
