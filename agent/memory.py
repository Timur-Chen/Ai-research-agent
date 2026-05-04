import logging

logger = logging.getLogger(__name__)


class AgentMemory:
    """
    In-memory key-value store scoped to a single agent session.
    The agent loop uses this to persist named values across reasoning steps
    without re-fetching information it has already obtained.
    """

    def __init__(self):
        self._store: dict[str, str] = {}

    def set(self, key: str, value: str) -> None:
        logger.debug(f"AgentMemory.set: {key}")
        self._store[key] = value

    def get(self, key: str) -> str | None:
        return self._store.get(key)

    def all(self) -> dict[str, str]:
        return dict(self._store)

    def clear(self) -> None:
        self._store.clear()
        logger.debug("AgentMemory cleared.")
