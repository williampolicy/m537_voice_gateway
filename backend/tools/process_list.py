"""
M537 Voice Gateway - Process List Tool
Provides running process information
"""
import subprocess
from typing import Dict, Any

from tools.base_tool import BaseTool


class ProcessListTool(BaseTool):
    """Tool to get running process information"""

    name = "process_list"
    description = "获取运行中的进程列表"

    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute process list query"""
        try:
            # Get top processes by CPU
            cpu_result = subprocess.run(
                ["ps", "aux", "--sort=-%cpu"],
                capture_output=True,
                text=True,
                timeout=10
            )

            top_cpu = []
            lines = cpu_result.stdout.strip().split("\n")
            for line in lines[1:11]:  # Top 10 by CPU
                parts = line.split(None, 10)
                if len(parts) >= 11:
                    top_cpu.append({
                        "user": parts[0],
                        "pid": parts[1],
                        "cpu": parts[2],
                        "mem": parts[3],
                        "command": parts[10][:50]  # Truncate command
                    })

            # Get top processes by memory
            mem_result = subprocess.run(
                ["ps", "aux", "--sort=-%mem"],
                capture_output=True,
                text=True,
                timeout=10
            )

            top_mem = []
            lines = mem_result.stdout.strip().split("\n")
            for line in lines[1:11]:  # Top 10 by memory
                parts = line.split(None, 10)
                if len(parts) >= 11:
                    top_mem.append({
                        "user": parts[0],
                        "pid": parts[1],
                        "cpu": parts[2],
                        "mem": parts[3],
                        "command": parts[10][:50]
                    })

            # Get total process count
            count_result = subprocess.run(
                ["ps", "aux"],
                capture_output=True,
                text=True,
                timeout=10
            )
            total_count = len(count_result.stdout.strip().split("\n")) - 1

            # Get zombie processes
            zombie_result = subprocess.run(
                ["ps", "aux"],
                capture_output=True,
                text=True,
                timeout=10
            )
            zombie_count = sum(1 for line in zombie_result.stdout.split("\n") if " Z " in line)

            return {
                "success": True,
                "total_processes": total_count,
                "zombie_processes": zombie_count,
                "top_cpu": top_cpu[:5],
                "top_memory": top_mem[:5]
            }

        except subprocess.TimeoutExpired:
            return {"success": False, "error": "命令执行超时"}
        except Exception as e:
            return {"success": False, "error": str(e)}
