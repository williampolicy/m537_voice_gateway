"""
M537 Voice Gateway - Service Logs Tool
Provides recent log entries for services
"""
import subprocess
import os
from typing import Dict, Any, List
from datetime import datetime

from tools.base_tool import BaseTool
from settings import settings


class ServiceLogsTool(BaseTool):
    """Tool to get recent service logs"""

    name = "service_logs"
    description = "获取服务日志"

    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute service logs query"""
        try:
            service = params.get("service", "all")
            lines = params.get("lines", 20)

            if service == "all":
                return self._get_system_logs(lines)
            else:
                return self._get_service_logs(service, lines)

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _get_system_logs(self, lines: int) -> Dict[str, Any]:
        """Get recent system logs"""
        logs = []

        # Try journalctl for systemd logs
        try:
            journal_result = subprocess.run(
                ["journalctl", "-n", str(lines), "--no-pager", "-p", "err..warning"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if journal_result.returncode == 0:
                for line in journal_result.stdout.strip().split("\n")[-lines:]:
                    if line.strip():
                        logs.append({
                            "source": "journalctl",
                            "message": line[:200],
                            "level": "warning"
                        })
        except Exception:
            pass

        # Check Docker logs if available
        try:
            docker_result = subprocess.run(
                ["docker", "ps", "--format", "{{.Names}}"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if docker_result.returncode == 0:
                containers = docker_result.stdout.strip().split("\n")[:5]
                for container in containers:
                    if container:
                        log_result = subprocess.run(
                            ["docker", "logs", "--tail", "5", container],
                            capture_output=True,
                            text=True,
                            timeout=5
                        )
                        if log_result.stderr:  # Docker outputs logs to stderr
                            for line in log_result.stderr.strip().split("\n")[-3:]:
                                if line.strip():
                                    logs.append({
                                        "source": f"docker:{container}",
                                        "message": line[:150],
                                        "level": "info"
                                    })
        except Exception:
            pass

        return {
            "success": True,
            "log_entries": logs[:lines],
            "total_entries": len(logs),
            "timestamp": datetime.now().isoformat()
        }

    def _get_service_logs(self, service: str, lines: int) -> Dict[str, Any]:
        """Get logs for a specific service"""
        logs = []

        # Check if it's a Docker container
        try:
            log_result = subprocess.run(
                ["docker", "logs", "--tail", str(lines), service],
                capture_output=True,
                text=True,
                timeout=10
            )
            if log_result.returncode == 0:
                output = log_result.stderr or log_result.stdout
                for line in output.strip().split("\n"):
                    if line.strip():
                        logs.append({
                            "source": f"docker:{service}",
                            "message": line[:200],
                            "level": "info"
                        })
                return {
                    "success": True,
                    "service": service,
                    "log_entries": logs,
                    "total_entries": len(logs)
                }
        except Exception:
            pass

        # Try systemd service
        try:
            journal_result = subprocess.run(
                ["journalctl", "-u", service, "-n", str(lines), "--no-pager"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if journal_result.returncode == 0:
                for line in journal_result.stdout.strip().split("\n"):
                    if line.strip():
                        logs.append({
                            "source": f"systemd:{service}",
                            "message": line[:200],
                            "level": "info"
                        })
                return {
                    "success": True,
                    "service": service,
                    "log_entries": logs,
                    "total_entries": len(logs)
                }
        except Exception:
            pass

        return {
            "success": False,
            "error": f"未找到服务: {service}"
        }
