"""
Exercise 1 — Your first agent.

Goal: build the smallest possible agent from the shared provider factory and
ask it one question. See README.md for the full brief.

Run:

    uv run python -m exercises.first_agent.exercise "What is Azure App Service, in one sentence?"

Then compare against solution.py.
"""

from __future__ import annotations

import asyncio
import sys

from agent_framework import Agent

from providers import create_chat_client


def create_agent() -> Agent:
    """
    TODO 1: build and return an `Agent`.

    Use `create_chat_client()` for the client — it reads LLM_PROVIDER from
    lab/.env and returns the right chat client, whichever provider you picked.
    Give the agent a `name` and `instructions` describing what it should help
    with.
    """
    raise NotImplementedError("TODO 1: build the Agent")


async def ask(agent: Agent, prompt: str) -> str:
    """
    TODO 2: run `prompt` against `agent` and return the answer text.

    `await agent.run(prompt)` returns a result whose `.text` is the answer.
    """
    raise NotImplementedError("TODO 2: run the agent and return its answer")


async def main(prompt: str) -> None:
    agent = create_agent()
    print(await ask(agent, prompt))


if __name__ == "__main__":
    from config import ConfigError

    question = " ".join(sys.argv[1:]) or "What is Azure App Service, in one sentence?"
    try:
        asyncio.run(main(question))
    except ConfigError as error:
        sys.exit(f"\n{error}")
