"""
M537 Voice Gateway - Intent Parser Service
Parses user input to identify intent and extract parameters
"""
from typing import Optional, Dict, Any, List, Tuple
import re
import logging

from config.intent_rules import INTENT_RULES

logger = logging.getLogger(__name__)


class IntentParser:
    """
    Intent parser using rule-based matching.
    Rules take priority over LLM for stability and auditability.
    """

    def __init__(self):
        self.rules = INTENT_RULES

    def parse(self, transcript: str) -> Tuple[Optional[str], float, Dict[str, Any]]:
        """
        Parse user input to identify intent.

        Args:
            transcript: User's speech transcript

        Returns:
            Tuple of (intent, confidence, params)
        """
        transcript_lower = transcript.lower().strip()

        # Step 1: Rule-based matching (priority)
        for intent, rule in self.rules.items():
            for keyword in rule.get("keywords", []):
                if keyword.lower() in transcript_lower:
                    params = self._extract_params(transcript, rule.get("params", []))
                    logger.debug(f"Matched intent: {intent} with keyword: {keyword}")
                    return intent, 0.95, params

        # Step 2: Pattern matching for specific queries
        intent, params = self._pattern_match(transcript_lower)
        if intent:
            return intent, 0.85, params

        # Not recognized
        return None, 0.0, {}

    def _extract_params(self, transcript: str, param_types: List[str]) -> Dict[str, Any]:
        """Extract parameters from transcript"""
        params = {}

        if "project_id" in param_types:
            project_id = self._extract_project_id(transcript)
            if project_id:
                params["project_id"] = project_id

        if "days" in param_types:
            days = self._extract_days(transcript)
            if days:
                params["days"] = days

        return params

    def _extract_project_id(self, transcript: str) -> Optional[str]:
        """Extract and normalize project ID from transcript"""
        # Various patterns for project IDs
        patterns = [
            r'[mM]\s*(\d+)',           # m536, m 536
            r'项目\s*[mM]?\s*(\d+)',    # 项目536, 项目m536
            r'[mM](\d)\s+(\d+)',        # m5 36 -> m536
        ]

        for pattern in patterns:
            match = re.search(pattern, transcript)
            if match:
                if len(match.groups()) == 2:
                    project_id = f"m{match.group(1)}{match.group(2)}"
                else:
                    project_id = f"m{match.group(1)}"
                return self._normalize_project_id(project_id)

        # Chinese number patterns
        chinese_patterns = {
            r'[mM]\s*五三六': 'm536',
            r'[mM]\s*五百三十六': 'm536',
            r'[mM]\s*八千': 'm8000',
            r'[mM]\s*五二零': 'm520',
        }

        for pattern, result in chinese_patterns.items():
            if re.search(pattern, transcript):
                return result

        return None

    def _normalize_project_id(self, project_id: str) -> str:
        """Normalize project ID format"""
        # Ensure lowercase 'm' prefix
        project_id = project_id.lower()
        if not project_id.startswith('m'):
            project_id = 'm' + project_id
        return project_id

    def _extract_days(self, transcript: str) -> Optional[int]:
        """Extract number of days from transcript"""
        patterns = [
            (r'(\d+)\s*天', lambda m: int(m.group(1))),
            (r'(\d+)\s*日', lambda m: int(m.group(1))),
            (r'(\d+)\s*小时', lambda m: int(m.group(1)) // 24),
            (r'一周', lambda m: 7),
            (r'本周', lambda m: 7),
            (r'这周', lambda m: 7),
        ]

        for pattern, extractor in patterns:
            match = re.search(pattern, transcript)
            if match:
                return extractor(match)

        return None

    def _pattern_match(self, transcript: str) -> Tuple[Optional[str], Dict[str, Any]]:
        """Additional pattern-based matching"""
        # Project summary query
        if re.search(r'是什么|是啥|介绍|简介|描述', transcript):
            project_id = self._extract_project_id(transcript)
            if project_id:
                return "project_summary", {"project_id": project_id}

        return None, {}

    def get_suggestions(self) -> List[str]:
        """Get available query suggestions"""
        return [
            "现在有多少个项目？",
            "系统状态怎么样？",
            "当前有哪些端口在监听？",
            "最近有什么错误？",
            "m536 是什么项目？"
        ]

    def get_related_suggestions(self, intent: str) -> List[str]:
        """Get related suggestions based on current intent"""
        related = {
            "count_projects": [
                "哪些是 P0 项目？",
                "最近更新了哪些项目？"
            ],
            "system_status": [
                "当前有哪些端口在监听？",
                "哪些 Docker 容器在运行？"
            ],
            "list_ports": [
                "哪些 Docker 容器在运行？",
                "系统状态怎么样？"
            ],
            "list_containers": [
                "系统状态怎么样？",
                "P0 服务状态如何？"
            ],
            "recent_errors": [
                "P0 服务状态如何？",
                "系统状态怎么样？"
            ],
            "project_summary": [
                "最近更新了哪些项目？",
                "哪些项目没有 README？"
            ]
        }
        return related.get(intent, self.get_suggestions()[:2])
