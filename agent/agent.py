import logging

import anthropic

import config
from agent.memory import AgentMemory
from agent.prompts import SYSTEM_PROMPT
from tools import REGISTRY
from tools.schemas import ToolResult

# Import tool modules so they self-register via the @register decorator
import tools.calculator      # noqa: F401
import tools.file_reader     # noqa: F401
import tools.memory_store    # noqa: F401
import tools.web_search      # noqa: F401

logger = logging.getLogger(__name__)


class ReactAgent:
    """
    A ReAct (Reasoning + Acting) agent that uses the Anthropic Messages API
    and a registry of Python tools to answer user queries step by step.
    """

    def __init__(self, max_iterations: int = config.MAX_ITERATIONS):
        self.client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
        self.max_iterations = max_iterations
        self.messages: list[dict] = []
        self.memory = AgentMemory()

    def run(self, query: str) -> str:
        """
        Run the ReAct loop for the given query and return the agent's final answer.
        The loop continues until the model emits a FINAL ANSWER or the iteration
        limit is reached.
        """
        logger.info(f"Agent starting  query={query!r}")
        self.messages.append({"role": "user", "content": query})

        for iteration in range(1, self.max_iterations + 1):
            logger.info(f"--- Iteration {iteration}/{self.max_iterations} ---")
            response = self._call_api()

            if response.stop_reason == "tool_use":
                # The model wants to call one or more tools
                tool_results = self._dispatch_tools(response.content)
                self.messages.append({"role": "assistant", "content": response.content})
                self.messages.append({"role": "user", "content": tool_results})

            else:
                # The model produced a text response
                text = self._extract_text(response.content)
                logger.info(f"Agent text: {text[:120]}...")
                self.messages.append({"role": "assistant", "content": text})

                if "FINAL ANSWER" in text:
                    answer = text.split("FINAL ANSWER")[-1].strip().lstrip(":").strip()
                    logger.info("Agent reached FINAL ANSWER.")
                    return answer

        return "Maximum iterations reached without a final answer."

    # ── Private helpers ───────────────────────────────────────────────────────

    def _call_api(self):
        """Send the current conversation to the Anthropic API and return the response."""
        return self.client.messages.create(
            model=config.MODEL_ID,
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            tools=REGISTRY.get_schemas(),
            messages=self.messages,
        )

    def _dispatch_tools(self, content: list) -> list[dict]:
        """
        Find all tool_use blocks in the API response content, call the matching
        tool for each, and return a list of tool_result blocks for the next API call.
        """
        results = []
        for block in content:
            if block.type == "tool_use":
                logger.info(f"Tool call: {block.name}  input={block.input}")
                result: ToolResult = REGISTRY.dispatch(block.name, **block.input)
                logger.debug(
                    f"Tool result: success={result.success}  "
                    f"output={result.output[:80]!r}"
                )
                results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result.to_api_content(),
                    }
                )
        return results

    def _extract_text(self, content: list) -> str:
        """Concatenate all text blocks from the API response content."""
        return "\n".join(
            block.text for block in content if hasattr(block, "text")
        )
