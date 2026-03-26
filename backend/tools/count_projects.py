"""
M537 Voice Gateway - Count Projects Tool
Counts total projects in the projects directory
"""
import os
from typing import Dict, Any

from tools.base_tool import BaseTool
from settings import settings


class CountProjectsTool(BaseTool):
    """Count projects in the projects directory"""

    name = "count_projects"
    description = "统计服务器上的项目总数"

    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        base_path = settings.PROJECTS_BASE_PATH

        total = 0
        p0, p1, p2, p3 = 0, 0, 0, 0

        if not os.path.exists(base_path):
            return {"total": 0, "p0": 0, "p1": 0, "p2": 0, "p3": 0}

        for item in os.listdir(base_path):
            item_path = os.path.join(base_path, item)

            # Only count directories starting with 'm' followed by digits
            if os.path.isdir(item_path) and item.startswith("m") and len(item) > 1:
                # Extract numeric part
                num_part = item[1:]
                if num_part.isdigit() or (num_part.replace("_", "").replace("-", "")[:4].isdigit()):
                    total += 1

                    # Classify by priority (based on project number)
                    try:
                        # Extract first numeric portion
                        num_str = ""
                        for c in num_part:
                            if c.isdigit():
                                num_str += c
                            else:
                                break
                        num = int(num_str) if num_str else 9999

                        if num < 100:
                            p0 += 1
                        elif num < 500:
                            p1 += 1
                        elif num < 1000:
                            p2 += 1
                        else:
                            p3 += 1
                    except ValueError:
                        p3 += 1

        return {
            "total": total,
            "p0": p0,
            "p1": p1,
            "p2": p2,
            "p3": p3
        }
