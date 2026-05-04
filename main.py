"""
main.py — CLI entry point for the AI Research & Task Assistant.

Usage examples:
    python main.py --query "What is 17 * 34?"
    python main.py --query "Read the file data.csv and summarise it" --verbose
    python main.py --query "Search for the latest Python version" --max-iter 5
"""

import argparse
import logging
import sys

import config
from agent.agent import ReactAgent


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="AI Research & Task Assistant — a ReAct agent powered by Claude."
    )
    parser.add_argument(
        "--query", "-q",
        type=str,
        default="",
        help="The question or task to send to the agent.",
    )
    parser.add_argument(
        "--max-iter",
        type=int,
        default=config.MAX_ITERATIONS,
        help=f"Maximum number of reasoning iterations (default: {config.MAX_ITERATIONS}).",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable DEBUG-level logging to see every tool call and result.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    query = args.query.strip()
    if not query:
        try:
            query = input("Enter your query: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nAborted.")
            sys.exit(0)

    if not query:
        print("Error: query cannot be empty.", file=sys.stderr)
        sys.exit(1)

    agent = ReactAgent(max_iterations=args.max_iter)
    result = agent.run(query)

    print("\n" + "=" * 60)
    print("RESULT")
    print("=" * 60)
    print(result)
    print("=" * 60)


if __name__ == "__main__":
    main()
