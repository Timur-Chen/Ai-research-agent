"""
conftest.py — shared pytest fixtures used across test_tools.py and test_agent.py.
"""

import pytest
from unittest.mock import MagicMock, patch

from tools.memory_store import _store


@pytest.fixture(autouse=False)
def clear_memory_store():
    """Reset the in-memory store before each test that requests this fixture."""
    _store.clear()
    yield
    _store.clear()


@pytest.fixture
def mock_anthropic_client():
    """Return a MagicMock that replaces anthropic.Anthropic for agent tests."""
    with patch("agent.agent.anthropic.Anthropic") as mock_class:
        mock_client = MagicMock()
        mock_class.return_value = mock_client
        yield mock_client
