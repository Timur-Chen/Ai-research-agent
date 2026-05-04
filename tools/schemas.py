from dataclasses import dataclass


@dataclass
class ToolResult:
    """Standard return type for every tool in the registry."""

    success: bool
    output: str
    error: str | None = None

    def to_api_content(self) -> str:
        """Format the result for the Anthropic tool_result content block."""
        if self.success:
            return self.output
        return f"ERROR: {self.error}"
