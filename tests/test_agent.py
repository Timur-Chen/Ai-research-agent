"""
test_agent.py — integration tests for the ReactAgent loop.

The Anthropic API is patched with unittest.mock so no real API key is needed.
Run with:  pytest tests/test_agent.py -v
"""

from unittest.mock import MagicMock, patch

import pytest

from agent.agent import ReactAgent


def _make_text_response(text: str, stop_reason: str = "end_turn"):
    """Helper: build a mock Anthropic response that contains a single text block."""
    block = MagicMock()
    block.type = "text"
    block.text = text
    response = MagicMock()
    response.stop_reason = stop_reason
    response.content = [block]
    return response


def _make_tool_response(tool_name: str, tool_input: dict, tool_id: str = "tool_1"):
    """Helper: build a mock Anthropic response with a tool_use block."""
    block = MagicMock()
    block.type = "tool_use"
    block.name = tool_name
    block.input = tool_input
    block.id = tool_id
    response = MagicMock()
    response.stop_reason = "tool_use"
    response.content = [block]
    return response


class TestReactAgent:
    @patch("agent.agent.anthropic.Anthropic")
    def test_returns_final_answer(self, mock_class):
        mock_client = MagicMock()
        mock_class.return_value = mock_client
        mock_client.messages.create.return_value = _make_text_response(
            "Thought: I know the answer.\nFINAL ANSWER: 42"
        )
        agent = ReactAgent(max_iterations=3)
        result = agent.run("What is 6 times 7?")
        assert "42" in result

    @patch("agent.agent.anthropic.Anthropic")
    def test_max_iterations_reached(self, mock_class):
        mock_client = MagicMock()
        mock_class.return_value = mock_client
        mock_client.messages.create.return_value = _make_text_response(
            "Thought: Still thinking..."
        )
        agent = ReactAgent(max_iterations=2)
        result = agent.run("An unanswerable question")
        assert "Maximum iterations" in result

    @patch("agent.agent.anthropic.Anthropic")
    def test_tool_call_then_final_answer(self, mock_class):
        mock_client = MagicMock()
        mock_class.return_value = mock_client

        # First call: model wants to use the calculator
        tool_response = _make_tool_response("calculator_tool", {"expression": "6 * 7"})
        # Second call: model gives final answer after seeing the tool result
        final_response = _make_text_response("FINAL ANSWER: 6 times 7 is 42.")

        mock_client.messages.create.side_effect = [tool_response, final_response]

        agent = ReactAgent(max_iterations=5)
        result = agent.run("What is 6 times 7?")
        assert "42" in result
        assert mock_client.messages.create.call_count == 2

    @patch("agent.agent.anthropic.Anthropic")
    def test_messages_list_grows_correctly(self, mock_class):
        mock_client = MagicMock()
        mock_class.return_value = mock_client
        mock_client.messages.create.return_value = _make_text_response(
            "FINAL ANSWER: Done."
        )
        agent = ReactAgent(max_iterations=3)
        agent.run("Hello")
        # messages should contain: user query + assistant response
        assert len(agent.messages) >= 2
        assert agent.messages[0]["role"] == "user"
