"""
M537 Voice Gateway - Uptime Info Tool
Provides system uptime and load information
"""
import subprocess
from typing import Dict, Any
from datetime import datetime, timedelta

from tools.base_tool import BaseTool


class UptimeInfoTool(BaseTool):
    """Tool to get system uptime information"""

    name = "uptime_info"
    description = "获取系统运行时间和负载"

    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute uptime query"""
        try:
            # Get uptime
            with open("/proc/uptime", "r") as f:
                uptime_seconds = float(f.read().split()[0])

            uptime_delta = timedelta(seconds=int(uptime_seconds))
            days = uptime_delta.days
            hours, remainder = divmod(uptime_delta.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)

            # Get load averages
            with open("/proc/loadavg", "r") as f:
                loadavg = f.read().split()[:3]

            load_1, load_5, load_15 = map(float, loadavg)

            # Get CPU count for load context
            cpu_count = 0
            with open("/proc/cpuinfo", "r") as f:
                cpu_count = sum(1 for line in f if line.startswith("processor"))

            # Determine load status
            load_ratio = load_1 / max(cpu_count, 1)
            if load_ratio < 0.7:
                load_status = "正常"
            elif load_ratio < 1.0:
                load_status = "较高"
            else:
                load_status = "过载"

            # Get logged in users
            who_result = subprocess.run(
                ["who"],
                capture_output=True,
                text=True,
                timeout=5
            )
            user_count = len([l for l in who_result.stdout.strip().split("\n") if l])

            # Get last boot time
            boot_time = datetime.now() - uptime_delta

            return {
                "success": True,
                "uptime": {
                    "days": days,
                    "hours": hours,
                    "minutes": minutes,
                    "total_seconds": int(uptime_seconds),
                    "human_readable": f"{days}天{hours}小时{minutes}分钟"
                },
                "load_average": {
                    "1min": load_1,
                    "5min": load_5,
                    "15min": load_15,
                    "status": load_status
                },
                "cpu_count": cpu_count,
                "logged_in_users": user_count,
                "boot_time": boot_time.strftime("%Y-%m-%d %H:%M:%S")
            }

        except Exception as e:
            return {"success": False, "error": str(e)}
