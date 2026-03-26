"""
M537 Voice Gateway - Query Executor Service
Executes queries using whitelist tools
"""
from typing import Dict, Any
import importlib
import logging

from config.tool_registry import TOOL_REGISTRY

logger = logging.getLogger(__name__)


class QueryExecutor:
    """
    Query executor that calls whitelist tools.
    Only registered tools can be executed for security.
    """

    def __init__(self):
        self.tools = {}
        self._load_tools()

    def _load_tools(self):
        """Load all registered tools"""
        for tool_name, tool_info in TOOL_REGISTRY.items():
            try:
                module = importlib.import_module(f"tools.{tool_info['module']}")
                tool_class = getattr(module, tool_info['class'])
                self.tools[tool_name] = tool_class()
                logger.info(f"Loaded tool: {tool_name}")
            except Exception as e:
                logger.error(f"Failed to load tool {tool_name}: {e}")

    def execute(self, tool_name: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Execute a tool query.

        Args:
            tool_name: Name of the tool to execute
            params: Parameters for the tool

        Returns:
            Dict with success, data, and error fields
        """
        if tool_name not in self.tools:
            logger.warning(f"Unknown tool requested: {tool_name}")
            return {
                "success": False,
                "data": None,
                "error": f"未知的查询类型: {tool_name}"
            }

        try:
            tool = self.tools[tool_name]
            result = tool.execute(params or {})
            return {
                "success": True,
                "data": result,
                "error": None
            }
        except Exception as e:
            logger.error(f"Tool execution failed {tool_name}: {e}")
            return {
                "success": False,
                "data": None,
                "error": str(e)
            }

    def list_available_tools(self) -> Dict[str, str]:
        """List available tools"""
        return {name: info["description"] for name, info in TOOL_REGISTRY.items()}

    def is_tool_available(self, tool_name: str) -> bool:
        """Check if a tool is available"""
        return tool_name in self.tools
