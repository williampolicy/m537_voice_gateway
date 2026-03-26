"""
M537 Voice Gateway - List Ports Tool
Lists listening ports on the system
"""
import subprocess
from typing import Dict, Any, List

from tools.base_tool import BaseTool


class ListPortsTool(BaseTool):
    """List listening network ports"""

    name = "list_ports"
    description = "列出当前系统监听的端口"

    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        try:
            # Use ss command to get listening ports
            result = subprocess.run(
                ["ss", "-tuln"],
                capture_output=True,
                text=True,
                timeout=10
            )

            ports = self._parse_ports(result.stdout)

            # Format port list
            port_list = sorted(ports)[:15]  # Limit to 15 ports
            ports_str = ", ".join(map(str, port_list))

            return {
                "count": len(ports),
                "ports": ports_str,
                "all_ports": sorted(ports)
            }
        except subprocess.TimeoutExpired:
            return {"count": 0, "ports": "", "error": "命令超时"}
        except Exception as e:
            return {"count": 0, "ports": "", "error": str(e)}

    def _parse_ports(self, output: str) -> List[int]:
        """Parse ss output to extract port numbers"""
        ports = set()

        for line in output.strip().split("\n")[1:]:  # Skip header
            parts = line.split()
            if len(parts) >= 5:
                local_addr = parts[4]
                # Format: 0.0.0.0:80 or [::]:80 or *:80
                if ":" in local_addr:
                    port_str = local_addr.rsplit(":", 1)[-1]
                    if port_str.isdigit():
                        port = int(port_str)
                        # Filter common system ports
                        if port > 0 and port < 65536:
                            ports.add(port)

        return list(ports)
