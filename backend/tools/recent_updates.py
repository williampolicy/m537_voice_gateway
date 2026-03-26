"""
M537 Voice Gateway - Recent Updates Tool
Lists recently updated projects
"""
import os
from datetime import datetime, timedelta
from typing import Dict, Any, List

from tools.base_tool import BaseTool
from settings import settings


class RecentUpdatesTool(BaseTool):
    """List recently updated projects"""

    name = "recent_updates"
    description = "查询最近更新的项目"

    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        days = params.get("days", 7)
        base_path = settings.PROJECTS_BASE_PATH
        updated = []

        if not os.path.exists(base_path):
            return {
                "count": 0,
                "projects": "",
                "days": days
            }

        cutoff = datetime.now() - timedelta(days=days)
        cutoff_ts = cutoff.timestamp()

        for item in os.listdir(base_path):
            item_path = os.path.join(base_path, item)

            # Only check directories starting with 'm'
            if os.path.isdir(item_path) and item.startswith("m"):
                try:
                    # Check modification time of key files
                    latest_mtime = 0

                    for root, dirs, files in os.walk(item_path):
                        # Skip hidden directories
                        dirs[:] = [d for d in dirs if not d.startswith('.')]

                        for file in files[:10]:  # Limit files checked
                            if file.startswith('.'):
                                continue
                            file_path = os.path.join(root, file)
                            try:
                                mtime = os.path.getmtime(file_path)
                                if mtime > latest_mtime:
                                    latest_mtime = mtime
                            except OSError:
                                continue

                        # Only check first few directories
                        if len(updated) > 20:
                            break

                    if latest_mtime > cutoff_ts:
                        updated.append({
                            "name": item,
                            "mtime": latest_mtime
                        })

                except Exception:
                    continue

        # Sort by modification time (most recent first)
        updated.sort(key=lambda x: x["mtime"], reverse=True)

        # Format for display
        display_list = [p["name"] for p in updated[:10]]
        projects_str = ", ".join(display_list)
        if len(updated) > 10:
            projects_str += f" 等共 {len(updated)} 个"

        return {
            "count": len(updated),
            "projects": projects_str,
            "days": days,
            "all_updated": [p["name"] for p in updated]
        }
