"""
test_tools.py — unit tests for all four implemented tools.

All tests are fully offline: no real API keys or network access required.
Run with:  pytest tests/test_tools.py -v
"""

import json
import pytest

from tools.calculator import calculator_tool
from tools.file_reader import file_reader_tool
from tools.memory_store import memory_store_tool, _store
from tools.schemas import ToolResult


# ── calculator_tool ───────────────────────────────────────────────────────────

class TestCalculatorTool:
    def test_basic_addition(self):
        result = calculator_tool("3 + 4")
        assert result.success is True
        assert result.output == "7"

    def test_basic_multiplication(self):
        result = calculator_tool("17 * 34")
        assert result.success is True
        assert result.output == "578"

    def test_order_of_operations(self):
        result = calculator_tool("3 + 4 * 2")
        assert result.success is True
        assert result.output == "11"

    def test_power(self):
        result = calculator_tool("2 ** 10")
        assert result.success is True
        assert result.output == "1024"

    def test_float_division(self):
        result = calculator_tool("10 / 4")
        assert result.success is True
        assert float(result.output) == pytest.approx(2.5)

    def test_modulo(self):
        result = calculator_tool("17 % 5")
        assert result.success is True
        assert result.output == "2"

    def test_nested_parentheses(self):
        result = calculator_tool("(2 + 3) * (4 - 1)")
        assert result.success is True
        assert result.output == "15"

    def test_division_by_zero(self):
        result = calculator_tool("5 / 0")
        assert result.success is False
        assert result.error is not None

    def test_rejects_import(self):
        result = calculator_tool('__import__("os").system("ls")')
        assert result.success is False

    def test_rejects_open_call(self):
        result = calculator_tool('open("secret.txt").read()')
        assert result.success is False

    def test_empty_expression(self):
        result = calculator_tool("")
        assert result.success is False

    def test_result_is_toolresult_instance(self):
        result = calculator_tool("1 + 1")
        assert isinstance(result, ToolResult)


# ── file_reader_tool ──────────────────────────────────────────────────────────

class TestFileReaderTool:
    def test_read_text_file(self, tmp_path):
        f = tmp_path / "hello.txt"
        f.write_text("Hello, world!")
        result = file_reader_tool(str(f))
        assert result.success is True
        assert result.output == "Hello, world!"

    def test_read_json_file(self, tmp_path):
        data = {"name": "Alice", "age": 30}
        f = tmp_path / "data.json"
        f.write_text(json.dumps(data))
        result = file_reader_tool(str(f))
        assert result.success is True
        parsed = json.loads(result.output)
        assert parsed["name"] == "Alice"

    def test_read_csv_file(self, tmp_path):
        f = tmp_path / "people.csv"
        f.write_text("name,age\nAlice,30\nBob,25\n")
        result = file_reader_tool(str(f))
        assert result.success is True
        rows = json.loads(result.output)
        assert len(rows) == 2
        assert rows[0]["name"] == "Alice"
        assert rows[1]["age"] == "25"

    def test_missing_file_returns_error(self):
        result = file_reader_tool("/nonexistent/path/file.txt")
        assert result.success is False
        assert "not found" in result.error.lower()

    def test_empty_text_file(self, tmp_path):
        f = tmp_path / "empty.txt"
        f.write_text("")
        result = file_reader_tool(str(f))
        assert result.success is True
        assert result.output == ""


# ── memory_store_tool ─────────────────────────────────────────────────────────

class TestMemoryStoreTool:
    def setup_method(self):
        _store.clear()

    def test_set_and_get(self):
        memory_store_tool("set", "city", "Tashkent")
        result = memory_store_tool("get", "city")
        assert result.success is True
        assert result.output == "Tashkent"

    def test_overwrite_existing_key(self):
        memory_store_tool("set", "lang", "Python")
        memory_store_tool("set", "lang", "Go")
        result = memory_store_tool("get", "lang")
        assert result.output == "Go"

    def test_get_missing_key(self):
        result = memory_store_tool("get", "nonexistent_key")
        assert result.success is False
        assert result.error is not None

    def test_invalid_action(self):
        result = memory_store_tool("delete", "city")
        assert result.success is False

    def test_set_returns_success(self):
        result = memory_store_tool("set", "k", "v")
        assert result.success is True

    def test_empty_value_allowed(self):
        memory_store_tool("set", "blank", "")
        result = memory_store_tool("get", "blank")
        assert result.success is True
        assert result.output == ""
