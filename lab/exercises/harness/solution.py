"""
Exercise 7 — Harness (solution).

Run:

    uv run python -m exercises.harness.solution "Draft a 3-step plan for adding a health-check endpoint to a Flask app"
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

from agent_framework import (
    Agent,
    AgentFileStore,
    FileSystemAgentFileStore,
    InMemoryHistoryProvider,
    create_harness_agent,
)

from providers import create_chat_client

FILE_MEMORY_DIR = Path(__file__).resolve().parent / ".harness-memory"

HARNESS_NAME = "LabHarness"

HARNESS_INSTRUCTIONS = (
    "You are working through a task that takes several steps. Plan before "
    "acting, keep your todo list current, and verify each step before "
    "moving on."
)

AGENT_INSTRUCTIONS = "You are a helpful assistant for developers working on backend services."


def create_file_memory() -> AgentFileStore:
    return FileSystemAgentFileStore(root_directory=FILE_MEMORY_DIR)


def create_harness() -> Agent:
    return create_harness_agent(
        client=create_chat_client(),
        name=HARNESS_NAME,
        harness_instructions=HARNESS_INSTRUCTIONS,
        agent_instructions=AGENT_INSTRUCTIONS,
        file_memory_store=create_file_memory(),
        history_provider=InMemoryHistoryProvider(load_messages=True),
        disable_web_search=True,
    )


async def main(task: str) -> None:
    async with create_harness() as harness:
        session = harness.create_session()
        result = await harness.run(task, session=session)
        print(result.text)


if __name__ == "__main__":
    from config import ConfigError

    prompt = " ".join(sys.argv[1:]) or (
        "Draft a 3-step plan for adding a health-check endpoint to a Flask app."
    )
    try:
        asyncio.run(main(prompt))
    except ConfigError as error:
        sys.exit(f"\n{error}")
