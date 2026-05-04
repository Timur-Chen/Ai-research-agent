import logging

from tools import register
from tools.schemas import ToolResult

logger = logging.getLogger(__name__)

# Session-scoped in-memory key-value store
_store: dict[str, str] = {}


@register
def memory_store_tool(action: str, key: str, value: str = "") -> ToolResult:
    """Store or retrieve a named value in the agent session memory. Use action='set' to store a value, action='get' to retrieve it."""
    try:
        logger.debug(f"memory_store_tool: action={action}  key={key}")
        if action == "set":
            _store[key] = value
            return ToolResult(success=True, output=f'Stored value under key "{key}".')
        if action == "get":
            if key not in _store:
                return ToolResult(
                    success=False,
                    output="",
                    error=f'Key "{key}" was not found in memory.',
                )
            return ToolResult(success=True, output=_store[key])
        return ToolResult(
            success=False,
            output="",
            error=f'Unknown action "{action}". Use "set" or "get".',
        )
    except Exception as e:
        logger.warning(f"memory_store_tool error: {e}")
        return ToolResult(success=False, output="", error=str(e))
