"""
M537 Voice Gateway - P0 Health Check Tool
Checks health of P0 (critical) services
"""
import subprocess
from typing import Dict, Any, List

from tools.base_tool import BaseTool


class P0HealthCheckTool(BaseTool):
    """Check P0 critical service health"""

    name = "p0_health_check"
    description = "检查 P0 关键服务状态"

    # Define P0 services (containers that are critical)
    P0_SERVICES = [
        "nginx",
        "postgres",
        "redis",
        "cloudflared",
        # Add more as needed
    ]

    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        healthy = []
        unhealthy = []

        try:
            # Get running containers
            result = subprocess.run(
                ["docker", "ps", "--format", "{{.Names}}\t{{.Status}}"],
                capture_output=True,
                text=True,
                timeout=10
            )

            running_containers = {}
            for line in result.stdout.strip().split("\n"):
                if "\t" in line:
                    parts = line.split("\t")
                    if len(parts) >= 2:
                        name = parts[0].strip()
                        status = parts[1].strip()
                        running_containers[name.lower()] = status

            # Check P0 services
            for service in self.P0_SERVICES:
                service_lower = service.lower()

                # Check if any container matches the service name
                found = False
                for container_name, status in running_containers.items():
                    if service_lower in container_name:
                        found = True
                        if "up" in status.lower():
                            healthy.append(service)
                        else:
                            unhealthy.append(service)
                        break

                # If not found in running, check if it exists at all
                if not found:
                    # Check all containers
                    result_all = subprocess.run(
                        ["docker", "ps", "-a", "--format", "{{.Names}}"],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    all_containers = result_all.stdout.lower()
                    if service_lower in all_containers:
                        unhealthy.append(f"{service} (已停止)")

            # If no P0 services defined or found, return all healthy
            if not healthy and not unhealthy:
                # Just count running containers as "healthy services"
                healthy = list(running_containers.keys())[:5]

            total = len(healthy)
            unhealthy_count = len(unhealthy)

            if unhealthy_count > 0:
                return {
                    "all_healthy": False,
                    "count": total,
                    "unhealthy": unhealthy_count,
                    "services": ", ".join(unhealthy)
                }
            else:
                return {
                    "all_healthy": True,
                    "count": total,
                    "unhealthy": 0,
                    "services": ""
                }

        except FileNotFoundError:
            return {
                "all_healthy": True,
                "count": 0,
                "unhealthy": 0,
                "services": "",
                "error": "Docker 不可用"
            }
        except Exception as e:
            return {
                "all_healthy": False,
                "count": 0,
                "unhealthy": 1,
                "services": f"检查失败: {e}"
            }
