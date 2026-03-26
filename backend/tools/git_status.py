"""
M537 Voice Gateway - Git Status Tool
Provides Git repository status for projects
"""
import subprocess
import os
from typing import Dict, Any, List

from tools.base_tool import BaseTool
from settings import settings


class GitStatusTool(BaseTool):
    """Tool to get Git repository status"""

    name = "git_status"
    description = "获取Git仓库状态"

    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute git status query"""
        try:
            base_path = settings.PROJECTS_BASE_PATH
            project_id = params.get("project_id")

            if project_id:
                # Single project status
                return self._get_project_git_status(base_path, project_id)
            else:
                # Summary of all projects
                return self._get_all_projects_summary(base_path)

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _get_project_git_status(self, base_path: str, project_id: str) -> Dict[str, Any]:
        """Get detailed git status for a single project"""
        # Find project directory
        project_dirs = []
        for item in os.listdir(base_path):
            if item.startswith(project_id) or item.lower().startswith(project_id.lower()):
                project_path = os.path.join(base_path, item)
                if os.path.isdir(project_path):
                    project_dirs.append(project_path)

        if not project_dirs:
            return {"success": False, "error": f"未找到项目: {project_id}"}

        project_path = project_dirs[0]
        git_path = os.path.join(project_path, ".git")

        if not os.path.exists(git_path):
            return {
                "success": True,
                "project_id": project_id,
                "is_git_repo": False,
                "message": "该项目不是Git仓库"
            }

        # Get git status
        status_result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=project_path,
            capture_output=True,
            text=True,
            timeout=10
        )

        # Get branch info
        branch_result = subprocess.run(
            ["git", "branch", "--show-current"],
            cwd=project_path,
            capture_output=True,
            text=True,
            timeout=10
        )

        # Get last commit
        log_result = subprocess.run(
            ["git", "log", "-1", "--format=%H|%s|%cr"],
            cwd=project_path,
            capture_output=True,
            text=True,
            timeout=10
        )

        # Parse status
        modified = []
        untracked = []
        for line in status_result.stdout.strip().split("\n"):
            if line:
                status = line[:2]
                file = line[3:]
                if "?" in status:
                    untracked.append(file)
                else:
                    modified.append(file)

        # Parse last commit
        last_commit = {}
        if log_result.returncode == 0 and log_result.stdout.strip():
            parts = log_result.stdout.strip().split("|")
            if len(parts) >= 3:
                last_commit = {
                    "hash": parts[0][:8],
                    "message": parts[1],
                    "relative_time": parts[2]
                }

        return {
            "success": True,
            "project_id": project_id,
            "is_git_repo": True,
            "branch": branch_result.stdout.strip(),
            "modified_files": modified[:10],  # Limit to 10
            "untracked_files": untracked[:10],
            "modified_count": len(modified),
            "untracked_count": len(untracked),
            "is_clean": len(modified) == 0 and len(untracked) == 0,
            "last_commit": last_commit
        }

    def _get_all_projects_summary(self, base_path: str) -> Dict[str, Any]:
        """Get git summary for all projects"""
        stats = {
            "total_projects": 0,
            "git_repos": 0,
            "clean_repos": 0,
            "dirty_repos": [],
            "non_git_projects": 0
        }

        for item in os.listdir(base_path):
            project_path = os.path.join(base_path, item)
            if not os.path.isdir(project_path):
                continue
            if item.startswith("."):
                continue

            stats["total_projects"] += 1
            git_path = os.path.join(project_path, ".git")

            if not os.path.exists(git_path):
                stats["non_git_projects"] += 1
                continue

            stats["git_repos"] += 1

            # Quick status check
            try:
                status_result = subprocess.run(
                    ["git", "status", "--porcelain"],
                    cwd=project_path,
                    capture_output=True,
                    text=True,
                    timeout=5
                )

                if status_result.stdout.strip():
                    change_count = len(status_result.stdout.strip().split("\n"))
                    stats["dirty_repos"].append({
                        "project": item,
                        "changes": change_count
                    })
                else:
                    stats["clean_repos"] += 1
            except Exception:
                pass

        # Sort dirty repos by change count
        stats["dirty_repos"] = sorted(
            stats["dirty_repos"],
            key=lambda x: x["changes"],
            reverse=True
        )[:10]  # Top 10

        return {
            "success": True,
            **stats
        }
