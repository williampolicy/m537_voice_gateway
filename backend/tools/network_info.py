"""
M537 Voice Gateway - Network Info Tool
Provides network connection information
"""
import subprocess
from typing import Dict, Any

from tools.base_tool import BaseTool


class NetworkInfoTool(BaseTool):
    """Tool to get network connection information"""

    name = "network_info"
    description = "获取网络连接信息"

    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute network info query"""
        try:
            # Get active connections count
            connections = {"established": 0, "listen": 0, "time_wait": 0, "close_wait": 0}

            ss_result = subprocess.run(
                ["ss", "-tan", "state", "established"],
                capture_output=True,
                text=True,
                timeout=10
            )
            connections["established"] = len(ss_result.stdout.strip().split("\n")) - 1

            ss_listen = subprocess.run(
                ["ss", "-tln"],
                capture_output=True,
                text=True,
                timeout=10
            )
            connections["listen"] = len(ss_listen.stdout.strip().split("\n")) - 1

            # Get network interfaces
            interfaces = []
            ip_result = subprocess.run(
                ["ip", "-o", "addr", "show"],
                capture_output=True,
                text=True,
                timeout=10
            )

            for line in ip_result.stdout.strip().split("\n"):
                parts = line.split()
                if len(parts) >= 4:
                    iface = parts[1]
                    if iface not in ["lo", "docker0"] and not iface.startswith("veth"):
                        addr_type = parts[2]
                        addr = parts[3].split("/")[0] if "/" in parts[3] else parts[3]
                        interfaces.append({
                            "interface": iface,
                            "type": addr_type,
                            "address": addr
                        })

            # Get public IP (if available)
            public_ip = None
            try:
                curl_result = subprocess.run(
                    ["curl", "-s", "--max-time", "3", "ifconfig.me"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if curl_result.returncode == 0:
                    public_ip = curl_result.stdout.strip()
            except Exception:
                pass

            return {
                "success": True,
                "connections": connections,
                "interfaces": interfaces,
                "public_ip": public_ip,
                "total_connections": sum(connections.values())
            }

        except subprocess.TimeoutExpired:
            return {"success": False, "error": "命令执行超时"}
        except Exception as e:
            return {"success": False, "error": str(e)}
