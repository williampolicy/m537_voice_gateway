"""
M537 Voice Gateway - List Containers Tool
Lists Docker containers on the system
"""
import subprocess
from typing import Dict, Any

from tools.base_tool import BaseTool


class ListContainersTool(BaseTool):
    """List Docker containers"""

    name = "list_containers"
    description = "列出运行中的Docker容器"

    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        try:
            # Get running containers
            result = subprocess.run(
                ["docker", "ps", "--format", "{{.Names}}"],
                capture_output=True,
                text=True,
                timeout=10
            )

            running_names = [n.strip() for n in result.stdout.strip().split("\n") if n.strip()]
            running = len(running_names)

            # Get all containers (including stopped)
            result_all = subprocess.run(
                ["docker", "ps", "-a", "--format", "{{.Names}}"],
                capture_output=True,
                text=True,
                timeout=10
            )

            all_names = [n.strip() for n in result_all.stdout.strip().split("\n") if n.strip()]
            total = len(all_names)
            stopped = total - running

            # Limit names to display
            display_names = running_names[:10]
            names_str = ", ".join(display_names)
            if len(running_names) > 10:
                names_str += f" 等 {len(running_names)} 个"

            return {
                "running": running,
                "stopped": stopped,
                "total": total,
                "names": names_str,
                "all_names": running_names
            }
        except FileNotFoundError:
            return {
                "running": 0,
                "stopped": 0,
                "total": 0,
                "names": "",
                "error": "Docker 未安装或不可用"
            }
        except subprocess.TimeoutExpired:
            return {
                "running": 0,
                "stopped": 0,
                "total": 0,
                "names": "",
                "error": "命令超时"
            }
        except Exception as e:
            return {
                "running": 0,
                "stopped": 0,
                "total": 0,
                "names": "",
                "error": str(e)
            }
