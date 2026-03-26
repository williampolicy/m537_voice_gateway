"""
M537 Voice Gateway - Query Executor Service
Executes queries using whitelist tools with caching
"""
from typing import Dict, Any
import importlib
import logging

from config.tool_registry import TOOL_REGISTRY
from services.cache import query_cache

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

    def execute(self, tool_name: str, params: Dict[str, Any] = None, use_cache: bool = True) -> Dict[str, Any]:
        """
        Execute a tool query with optional caching.

        Args:
            tool_name: Name of the tool to execute
            params: Parameters for the tool
            use_cache: Whether to use cache (default True)

        Returns:
            Dict with success, data, error, and cached fields
        """
        params = params or {}

        if tool_name not in self.tools:
            logger.warning(f"Unknown tool requested: {tool_name}")
            return {
                "success": False,
                "data": None,
                "error": f"未知的查询类型: {tool_name}",
                "cached": False
            }

        # Try cache first
        if use_cache:
            cached_data = query_cache.get(tool_name, params)
            if cached_data is not None:
                logger.debug(f"Cache hit for {tool_name}")
                return {
                    "success": True,
                    "data": cached_data,
                    "error": None,
                    "cached": True
                }

        try:
            tool = self.tools[tool_name]
            result = tool.execute(params)

            # Cache the result
            if use_cache:
                query_cache.set(tool_name, params, result)

            return {
                "success": True,
                "data": result,
                "error": None,
                "cached": False
            }
        except Exception as e:
            logger.error(f"Tool execution failed {tool_name}: {e}")
            return {
                "success": False,
                "data": None,
                "error": str(e),
                "cached": False
            }

    def list_available_tools(self) -> Dict[str, str]:
        """List available tools"""
        return {name: info["description"] for name, info in TOOL_REGISTRY.items()}

    def is_tool_available(self, tool_name: str) -> bool:
        """Check if a tool is available"""
        return tool_name in self.tools
