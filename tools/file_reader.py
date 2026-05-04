import csv
import json
import logging
import os

from tools import register
from tools.schemas import ToolResult

logger = logging.getLogger(__name__)


@register
def file_reader_tool(file_path: str) -> ToolResult:
    """Read a .txt, .csv, or .json file and return its contents as a string."""
    try:
        logger.debug(f"file_reader_tool: {file_path}")

        if not os.path.exists(file_path):
            return ToolResult(
                success=False,
                output="",
                error=f"File not found: {file_path}",
            )

        ext = os.path.splitext(file_path)[1].lower()

        if ext == ".csv":
            rows = []
            skipped = 0
            with open(file_path, newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    try:
                        rows.append(dict(row))
                    except Exception:
                        skipped += 1
            output = json.dumps(rows, indent=2)
            if skipped:
                output += f"\n\n(Warning: {skipped} malformed row(s) were skipped.)"
            return ToolResult(success=True, output=output)

        if ext == ".json":
            with open(file_path, encoding="utf-8") as f:
                data = json.load(f)
            return ToolResult(success=True, output=json.dumps(data, indent=2))

        # Default: plain text
        with open(file_path, encoding="utf-8") as f:
            content = f.read()
        return ToolResult(success=True, output=content)

    except Exception as e:
        logger.warning(f"file_reader_tool error: {e}")
        return ToolResult(success=False, output="", error=str(e))
