"""
M537 Voice Gateway - Disk Usage Tool
Provides detailed disk usage information
"""
import subprocess
from typing import Dict, Any

from tools.base_tool import BaseTool


class DiskUsageTool(BaseTool):
    """Tool to get detailed disk usage information"""

    name = "disk_usage"
    description = "获取详细的磁盘使用情况"

    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute disk usage query"""
        try:
            # Get disk usage with df
            df_result = subprocess.run(
                ["df", "-h", "--total"],
                capture_output=True,
                text=True,
                timeout=10
            )

            partitions = []
            lines = df_result.stdout.strip().split("\n")

            for line in lines[1:]:  # Skip header
                parts = line.split()
                if len(parts) >= 6:
                    filesystem = parts[0]
                    # Skip virtual filesystems
                    if filesystem.startswith(("tmpfs", "devtmpfs", "overlay", "shm")):
                        continue

                    partitions.append({
                        "filesystem": filesystem,
                        "size": parts[1],
                        "used": parts[2],
                        "available": parts[3],
                        "use_percent": parts[4],
                        "mounted_on": parts[5]
                    })

            # Get top space consumers in /data if exists
            large_dirs = []
            try:
                du_result = subprocess.run(
                    ["du", "-sh", "/data/projects/*"],
                    capture_output=True,
                    text=True,
                    timeout=30,
                    shell=True
                )

                if du_result.returncode == 0:
                    du_lines = du_result.stdout.strip().split("\n")
                    for line in sorted(du_lines, key=lambda x: x.split()[0], reverse=True)[:5]:
                        parts = line.split()
                        if len(parts) >= 2:
                            large_dirs.append({
                                "path": parts[1],
                                "size": parts[0]
                            })
            except Exception:
                pass

            # Calculate totals
            total_partition = next((p for p in partitions if p["filesystem"] == "total"), None)

            return {
                "success": True,
                "partitions": [p for p in partitions if p["filesystem"] != "total"],
                "total": total_partition,
                "large_directories": large_dirs,
                "partition_count": len([p for p in partitions if p["filesystem"] != "total"])
            }

        except subprocess.TimeoutExpired:
            return {"success": False, "error": "命令执行超时"}
        except Exception as e:
            return {"success": False, "error": str(e)}
