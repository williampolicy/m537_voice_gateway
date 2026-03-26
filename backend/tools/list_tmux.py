"""
M537 Voice Gateway - List Tmux Tool
Lists active tmux sessions
"""
import subprocess
from typing import Dict, Any

from tools.base_tool import BaseTool


class ListTmuxTool(BaseTool):
    """List tmux sessions"""

    name = "list_tmux"
    description = "列出 tmux 会话"

    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        try:
            result = subprocess.run(
                ["tmux", "list-sessions", "-F", "#{session_name}"],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode != 0:
                # No sessions or tmux not running
                if "no server running" in result.stderr.lower() or "no sessions" in result.stderr.lower():
                    return {
                        "count": 0,
                        "sessions": ""
                    }

            sessions = [s.strip() for s in result.stdout.strip().split("\n") if s.strip()]

            if not sessions:
                return {
                    "count": 0,
                    "sessions": ""
                }

            # Format sessions list
            sessions_str = ", ".join(sessions[:10])
            if len(sessions) > 10:
                sessions_str += f" 等共 {len(sessions)} 个"

            return {
                "count": len(sessions),
                "sessions": sessions_str,
                "all_sessions": sessions
            }

        except FileNotFoundError:
            return {
                "count": 0,
                "sessions": "",
                "error": "tmux 未安装"
            }
        except subprocess.TimeoutExpired:
            return {
                "count": 0,
                "sessions": "",
                "error": "命令超时"
            }
        except Exception as e:
            return {
                "count": 0,
                "sessions": "",
                "error": str(e)
            }
