"""
M537 Voice Gateway - Recent Errors Tool
Scans for recent errors in system logs
"""
import subprocess
from datetime import datetime, timedelta
from typing import Dict, Any

from tools.base_tool import BaseTool


class RecentErrorsTool(BaseTool):
    """Query recent errors from logs"""

    name = "recent_errors"
    description = "查询最近24小时的错误"

    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        hours = params.get("hours", 24)
        errors = []

        try:
            # Try to check docker logs for errors
            result = subprocess.run(
                ["docker", "ps", "--format", "{{.Names}}"],
                capture_output=True,
                text=True,
                timeout=5
            )

            container_names = [n.strip() for n in result.stdout.strip().split("\n") if n.strip()]

            # Check each container for recent errors
            for container in container_names[:5]:  # Limit to 5 containers
                try:
                    log_result = subprocess.run(
                        ["docker", "logs", "--tail", "100", "--since", f"{hours}h", container],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )

                    # Look for error patterns
                    for line in log_result.stderr.split("\n"):
                        if any(keyword in line.lower() for keyword in ["error", "exception", "failed", "critical"]):
                            errors.append(f"{container}: {line[:100]}")
                            if len(errors) >= 5:
                                break

                except Exception:
                    continue

        except Exception as e:
            pass

        # Also check system journal if available
        try:
            result = subprocess.run(
                ["journalctl", "-p", "err", "-n", "10", "--no-pager"],
                capture_output=True,
                text=True,
                timeout=5
            )

            for line in result.stdout.strip().split("\n")[:3]:
                if line.strip():
                    errors.append(f"系统: {line[:100]}")

        except Exception:
            pass

        if not errors:
            return {
                "count": 0,
                "errors": ""
            }

        # Format errors
        error_list = errors[:5]  # Limit to 5
        errors_str = "; ".join(error_list)

        return {
            "count": len(errors),
            "errors": errors_str[:500]  # Limit length
        }
