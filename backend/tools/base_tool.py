"""
M537 Voice Gateway - Base Tool Class
"""
from abc import ABC, abstractmethod
from typing import Dict, Any


class BaseTool(ABC):
    """Base class for all whitelist tools"""

    name: str = ""
    description: str = ""

    @abstractmethod
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the tool with given parameters"""
        pass

    def validate_params(self, params: Dict[str, Any], required: list) -> bool:
        """Validate that all required parameters are present"""
        return all(key in params for key in required)
