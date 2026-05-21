"""
Module 6 - Test Multi-Turn Conversations with OpsAgent

Run:
    python test_multi_turn_conversations.py
    or
    uv run test_multi_turn_conversations.py
"""

import asyncio
import argparse
import os

from dotenv import load_dotenv
from openai import AsyncOpenAI

from agent_framework import Agent
from agent_framework.openai import OpenAIChatCompletionClient

load_dotenv()

github_base_url = "https://models.github.ai/inference"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_MODEL = os.getenv("GITHUB_MODEL")

if not GITHUB_TOKEN or not GITHUB_MODEL:
    raise ValueError("GITHUB_TOKEN and GITHUB_MODEL must be set in the .env file")


def parse_args() -> argparse.Namespace:
    """Parse optional mode argument for session behavior."""

    parser = argparse.ArgumentParser(
        description="Run OpsAgent in session or stateless mode.",
    )
    parser.add_argument(
        "--mode",
        choices=["session", "stateless"],
        help="Execution mode. If omitted, an interactive choice is shown.",
    )
    return parser.parse_args()


def choose_mode(cli_mode: str | None) -> str:
    """Choose mode from CLI or interactive prompt."""

    if cli_mode:
        return cli_mode

    print("Choose mode:")
    print("  1) session   - remembers previous messages")
    print("  2) stateless - each turn is independent")

    while True:
        choice = input("Select mode (1/2): ").strip()
        if choice == "1":
            return "session"
        if choice == "2":
            return "stateless"
        print("Please enter 1 or 2.")


async def main():
    """Create and run OpsAgent in session or stateless mode."""

    args = parse_args()
    mode = choose_mode(args.mode)

    print(f"\n🤖 OpsAgent ({mode}) is ready.")
    print("Type 'exit' to stop.\n")

    async_openai = AsyncOpenAI(
        api_key=GITHUB_TOKEN,
        base_url=github_base_url,
    )

    client = OpenAIChatCompletionClient(
        model=GITHUB_MODEL,
        async_client=async_openai,
    )

    agent = Agent(
        client=client,
        name="OpsAgent",
        description="OpsAgent is an AI-powered operations and engineering assistant.",
        instructions=(
            "You are OpsAgent, an AI-powered operations and engineering assistant. "
            "Help developers and cloud engineers troubleshoot issues, retrieve documentation, "
            "analyze systems, and automate operational workflows. "
            "Keep responses concise, actionable, and practical. "
            "Use conversation context from earlier turns when relevant."
        ),
    )

    # In session mode, keep one session alive so prior turns are remembered.
    session = agent.create_session() if mode == "session" else None

    while True:
        try:
            query = input("👤 You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n👋 Goodbye!")
            break

        if not query:
            print("Please enter a message or type 'exit'.")
            continue

        if query.lower() in {"exit", "quit"}:
            print("👋 Goodbye!")
            break

        result = await agent.run(query, session=session)
        print(f"💬 OpsAgent: {result.text}\n")


if __name__ == "__main__":
    asyncio.run(main())
