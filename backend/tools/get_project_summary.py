"""
M537 Voice Gateway - Get Project Summary Tool
Reads project README to get summary
"""
import os
from typing import Dict, Any

from tools.base_tool import BaseTool
from settings import settings


class GetProjectSummaryTool(BaseTool):
    """Get project summary from README"""

    name = "get_project_summary"
    description = "读取项目 README 获取摘要"

    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        project_id = params.get("project_id")

        if not project_id:
            return {
                "not_found": True,
                "project_id": "未指定"
            }

        # Normalize project ID
        project_id = project_id.lower()
        if not project_id.startswith("m"):
            project_id = "m" + project_id

        project_path = os.path.join(settings.PROJECTS_BASE_PATH, project_id)

        # Try variations
        variations = [
            project_id,
            project_id.replace("m", "m_"),
        ]

        found_path = None
        for var in variations:
            path = os.path.join(settings.PROJECTS_BASE_PATH, var)
            if os.path.exists(path):
                found_path = path
                break

        # Also try pattern matching
        if not found_path and os.path.exists(settings.PROJECTS_BASE_PATH):
            for item in os.listdir(settings.PROJECTS_BASE_PATH):
                if item.lower().startswith(project_id):
                    found_path = os.path.join(settings.PROJECTS_BASE_PATH, item)
                    break

        if not found_path:
            return {
                "not_found": True,
                "project_id": project_id
            }

        # Look for README
        readme_names = ["README.md", "readme.md", "README", "readme.txt"]
        readme_path = None

        for name in readme_names:
            path = os.path.join(found_path, name)
            if os.path.exists(path):
                readme_path = path
                break

        if not readme_path:
            return {
                "project_id": project_id,
                "title": os.path.basename(found_path),
                "description": "该项目没有 README 文件。"
            }

        try:
            with open(readme_path, "r", encoding="utf-8") as f:
                content = f.read()

            title, description = self._extract_summary(content)

            return {
                "project_id": project_id,
                "title": title,
                "description": description
            }
        except Exception as e:
            return {
                "project_id": project_id,
                "title": os.path.basename(found_path),
                "description": f"读取 README 失败: {e}"
            }

    def _extract_summary(self, content: str) -> tuple:
        """Extract title and summary from README content"""
        lines = content.strip().split("\n")

        title = ""
        description = ""

        for line in lines:
            line = line.strip()

            # Find title (first H1)
            if line.startswith("# ") and not title:
                title = line[2:].strip()
            # Find description (first non-empty, non-heading line)
            elif line and not line.startswith("#") and not description:
                # Skip badges, links, empty formatting
                if not line.startswith("[") and not line.startswith(">") and not line.startswith("-"):
                    description = line[:200]  # Limit to 200 chars
                    break

        return title or "未命名项目", description or "暂无描述"
