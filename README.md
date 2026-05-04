# AI-Powered Research & Task Assistant

A ReAct (Reasoning + Acting) agent built in Python that accepts natural-language queries, reasons through them step by step, calls tools when needed, and returns a final answer.

---

## Features

- **ReAct agent loop** — the agent thinks, acts, observes, and repeats until it has a confident answer
- **Calculator tool** — evaluates arithmetic expressions safely using Python's `ast` module
- **File reader tool** — reads `.txt`, `.csv`, and `.json` files
- **Web search tool** — fetches real-time results via the Tavily Search API
- **Memory store tool** — holds named values in session memory across reasoning steps
- **CLI interface** — simple command-line usage with optional verbose logging

---

## Project Structure

```
ai_agent/
  agent/
    __init__.py
    agent.py          # ReactAgent class — main ReAct loop
    prompts.py        # System prompt
    memory.py         # AgentMemory — in-memory key-value store
  tools/
    __init__.py       # ToolRegistry + @register decorator
    schemas.py        # ToolResult dataclass
    calculator.py     # calculator_tool
    file_reader.py    # file_reader_tool
    web_search.py     # web_search_tool
    memory_store.py   # memory_store_tool
    summariser.py     # summarise() utility (Step 3 tool)
  tests/
    __init__.py
    conftest.py       # Shared fixtures
    test_tools.py     # Unit tests for all tools
    test_agent.py     # Integration tests with mocked API
  config.py           # Constants and environment variable loader
  main.py             # CLI entry point
  requirements.txt
  setup.sh
  .env.example
```

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/Timur-Chen/Ai-research-agent.git
cd ai-research-agent
```

### 2. Run the setup script (creates venv + installs dependencies)

```bash
bash setup.sh
source venv/bin/activate
```

Or manually:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

### 3. Add your API keys

Open `.env` and fill in your keys:

```
ANTHROPIC_API_KEY=your_anthropic_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
```

- Get an Anthropic API key at: https://console.anthropic.com
- Get a Tavily API key at: https://app.tavily.com

---

## Usage

```bash
# Basic query
python main.py --query "What is 17 * 34?"

# Web search
python main.py --query "What is the latest version of Python?"

# Read a local file
python main.py --query "Read the file data.csv and tell me how many rows it has"

# Verbose mode (shows every tool call and result)
python main.py --query "What is 100 / 4 + 7?" --verbose

# Custom iteration limit
python main.py --query "Explain quantum computing" --max-iter 5
```

---

## Running Tests

```bash
pytest tests/ -v
```

All tests are fully offline — no API keys or network access required.

---

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `ANTHROPIC_API_KEY` | Yes | API key for the Claude model |
| `TAVILY_API_KEY` | Yes (for web search) | API key for Tavily Search |

---

## Deployment

This system is designed to run as a **local command-line tool**. To deploy it on another machine:

1. Clone the repository
2. Run `bash setup.sh`
3. Fill in `.env` with valid API keys
4. Run `python main.py --query "your question"`

No server or container is required for local use.


## Step 2 Progress

### What was implemented

- `tools/calculator.py` — safe arithmetic evaluation using Python ast module
- `tools/file_reader.py` — reads .txt, .csv and .json files
- `tools/web_search.py` — real-time web search via Tavily API
- `tools/memory_store.py` — in-memory key-value store for agent session
- `agent/agent.py` — full ReAct loop with tool dispatch
- `tests/test_tools.py` — unit tests for all tools
- `tests/test_agent.py` — integration tests with mocked Anthropic API

### Design decisions made during Step 2

- Memory tool redesigned from file-based to in-memory storage
- code_executor_tool postponed to Step 3 (sandbox safety concerns)
- summariser_tool exists as utility function, full tool integration in Step 3

### How to run tests

```bash
pytest tests/ -v
```
