"""
M537 Voice Gateway - Cron Jobs Tool
Lists scheduled cron jobs
"""
import subprocess
import os
from typing import Dict, Any

from tools.base_tool import BaseTool


class CronJobsTool(BaseTool):
    """Tool to list cron jobs"""

    name = "cron_jobs"
    description = "列出定时任务"

    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute cron jobs query"""
        try:
            jobs = []

            # Get current user's crontab
            try:
                crontab_result = subprocess.run(
                    ["crontab", "-l"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if crontab_result.returncode == 0:
                    for line in crontab_result.stdout.strip().split("\n"):
                        line = line.strip()
                        if line and not line.startswith("#"):
                            jobs.append({
                                "source": "user_crontab",
                                "schedule": self._parse_schedule(line),
                                "command": self._parse_command(line),
                                "raw": line[:100]
                            })
            except Exception:
                pass

            # Check /etc/cron.d directory
            cron_d_path = "/etc/cron.d"
            if os.path.exists(cron_d_path):
                for filename in os.listdir(cron_d_path):
                    if filename.startswith("."):
                        continue
                    filepath = os.path.join(cron_d_path, filename)
                    try:
                        with open(filepath, "r") as f:
                            for line in f:
                                line = line.strip()
                                if line and not line.startswith("#") and not line.startswith("SHELL"):
                                    if len(line.split()) >= 6:
                                        jobs.append({
                                            "source": f"cron.d/{filename}",
                                            "schedule": self._parse_schedule(line),
                                            "command": self._parse_command(line),
                                            "raw": line[:100]
                                        })
                    except Exception:
                        pass

            # Check systemd timers
            try:
                timer_result = subprocess.run(
                    ["systemctl", "list-timers", "--no-pager", "--plain"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if timer_result.returncode == 0:
                    lines = timer_result.stdout.strip().split("\n")
                    for line in lines[1:]:  # Skip header
                        parts = line.split()
                        if len(parts) >= 5:
                            jobs.append({
                                "source": "systemd_timer",
                                "schedule": parts[0] if parts[0] != "n/a" else "inactive",
                                "command": parts[-1] if parts else "unknown",
                                "next_run": parts[0] if len(parts) > 0 else None
                            })
            except Exception:
                pass

            return {
                "success": True,
                "jobs": jobs[:20],  # Limit to 20
                "total_count": len(jobs)
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _parse_schedule(self, line: str) -> str:
        """Parse cron schedule from line"""
        parts = line.split()
        if len(parts) >= 5:
            schedule = " ".join(parts[:5])
            return self._humanize_schedule(schedule)
        return "unknown"

    def _parse_command(self, line: str) -> str:
        """Parse command from cron line"""
        parts = line.split()
        if len(parts) >= 6:
            # Skip user field if present (6+ fields might include user)
            cmd_start = 5 if len(parts) > 6 else 5
            return " ".join(parts[cmd_start:])[:80]
        return line[:80]

    def _humanize_schedule(self, schedule: str) -> str:
        """Convert cron schedule to human-readable format"""
        parts = schedule.split()
        if len(parts) != 5:
            return schedule

        minute, hour, day, month, weekday = parts

        # Common patterns
        if schedule == "* * * * *":
            return "每分钟"
        if schedule == "0 * * * *":
            return "每小时"
        if schedule == "0 0 * * *":
            return "每天午夜"
        if schedule == "0 0 * * 0":
            return "每周日午夜"
        if schedule == "0 0 1 * *":
            return "每月1日"

        # Build description
        desc = []
        if minute != "*":
            desc.append(f"第{minute}分")
        if hour != "*":
            desc.append(f"{hour}点")
        if day != "*":
            desc.append(f"每月{day}日")
        if weekday != "*":
            days = ["日", "一", "二", "三", "四", "五", "六"]
            if weekday.isdigit() and int(weekday) < 7:
                desc.append(f"周{days[int(weekday)]}")

        return " ".join(desc) if desc else schedule
