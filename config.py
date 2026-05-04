import logging
import os
from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
TAVILY_API_KEY = os.environ.get("TAVILY_API_KEY", "")
MODEL_ID = "claude-sonnet-4-20250514"
MAX_ITERATIONS = 10
LOG_LEVEL = logging.INFO

logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s  %(name)-20s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)
