import ast
import logging
import operator

from tools import register
from tools.schemas import ToolResult

logger = logging.getLogger(__name__)

# Only these AST node types are permitted inside an expression
SAFE_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


def _safe_eval(node):
    """
    Recursively evaluate an AST node using a whitelist of safe operations.
    Raises ValueError for any node type not on the whitelist.
    """
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in SAFE_OPS:
        left = _safe_eval(node.left)
        right = _safe_eval(node.right)
        return SAFE_OPS[type(node.op)](left, right)
    if isinstance(node, ast.UnaryOp) and type(node.op) in SAFE_OPS:
        return SAFE_OPS[type(node.op)](_safe_eval(node.operand))
    raise ValueError(f"Unsafe expression node: {type(node).__name__}")


@register
def calculator_tool(expression: str) -> ToolResult:
    """Evaluate a safe arithmetic expression and return the numeric result."""
    try:
        logger.debug(f"calculator_tool: {expression}")
        tree = ast.parse(expression.strip(), mode="eval")
        result = _safe_eval(tree.body)
        # Return integer string when result is whole number
        output = str(int(result)) if isinstance(result, float) and result.is_integer() else str(result)
        logger.debug(f"calculator_tool result: {output}")
        return ToolResult(success=True, output=output)
    except ZeroDivisionError:
        return ToolResult(success=False, output="", error="Division by zero.")
    except Exception as e:
        logger.warning(f"calculator_tool error: {e}")
        return ToolResult(success=False, output="", error=str(e))
