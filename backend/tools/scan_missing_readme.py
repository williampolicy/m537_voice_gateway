"""
M537 Voice Gateway - Scan Missing README Tool
Scans for projects without README files
"""
import os
from typing import Dict, Any, List

from tools.base_tool import BaseTool
from settings import settings


class ScanMissingReadmeTool(BaseTool):
    """Scan for projects missing README"""

    name = "scan_missing_readme"
    description = "扫描缺失 README 的项目"

    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        base_path = settings.PROJECTS_BASE_PATH
        missing = []
        total_checked = 0

        if not os.path.exists(base_path):
            return {
                "count": 0,
                "projects": "",
                "error": "项目目录不存在"
            }

        readme_names = ["README.md", "readme.md", "README", "readme.txt", "README.rst"]

        for item in os.listdir(base_path):
            item_path = os.path.join(base_path, item)

            # Only check directories starting with 'm'
            if os.path.isdir(item_path) and item.startswith("m"):
                total_checked += 1

                # Check for README
                has_readme = any(
                    os.path.exists(os.path.join(item_path, name))
                    for name in readme_names
                )

                if not has_readme:
                    missing.append(item)

        # Limit display
        display_list = missing[:10]
        projects_str = ", ".join(display_list)
        if len(missing) > 10:
            projects_str += f" 等共 {len(missing)} 个"

        return {
            "count": len(missing),
            "projects": projects_str,
            "all_missing": missing,
            "total_checked": total_checked
        }
