import inspect
import logging
from typing import get_type_hints

from tools.schemas import ToolResult

logger = logging.getLogger(__name__)


def _python_type_to_json(python_type) -> str:
    mapping = {
        str: "string",
        int: "integer",
        float: "number",
        bool: "boolean",
        list: "array",
        dict: "object",
    }
    return mapping.get(python_type, "string")


def _build_schema(func) -> dict:
    """Build an Anthropic-compatible JSON schema from a function's type hints and docstring."""
    hints = get_type_hints(func)
    hints.pop("return", None)
    sig = inspect.signature(func)
    doc = inspect.getdoc(func) or ""
    description = doc.split("\n")[0].strip()

    properties: dict = {}
    required: list = []

    for param_name, param in sig.parameters.items():
        python_type = hints.get(param_name, str)
        json_type = _python_type_to_json(python_type)
        properties[param_name] = {
            "type": json_type,
            "description": f"The {param_name} parameter.",
        }
        if param.default is inspect.Parameter.empty:
            required.append(param_name)

    return {
        "name": func.__name__,
        "description": description,
        "input_schema": {
            "type": "object",
            "properties": properties,
            "required": required,
        },
    }


class ToolRegistry:
    """Stores tool callables and their JSON schemas. Tools self-register at import time."""

    def __init__(self):
        self._tools: dict[str, dict] = {}

    def register(self, func):
        """Decorator: build schema from func and add it to the registry."""
        schema = _build_schema(func)
        self._tools[func.__name__] = {"func": func, "schema": schema}
        logger.debug(f"Registered tool: {func.__name__}")
        return func

    def get_schemas(self) -> list[dict]:
        """Return all tool schemas for passing to the Anthropic API."""
        return [v["schema"] for v in self._tools.values()]

    def dispatch(self, name: str, **kwargs) -> ToolResult:
        """Look up a tool by name and call it with the given keyword arguments."""
        entry = self._tools.get(name)
        if entry is None:
            logger.warning(f"Unknown tool requested: {name}")
            return ToolResult(success=False, output="", error=f"Unknown tool: {name}")
        logger.info(f"Dispatching tool: {name}  args={list(kwargs.keys())}")
        return entry["func"](**kwargs)


REGISTRY = ToolRegistry()
register = REGISTRY.register  # shorthand used by each tool module
