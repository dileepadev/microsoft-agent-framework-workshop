"""
Exercise 1 — Your first agent (solution).

Run:

    uv run python -m exercises.first_agent.solution "What is Azure App Service, in one sentence?"
"""

from __future__ import annotations

import asyncio
import sys

from agent_framework import Agent

from providers import create_chat_client


def create_agent() -> Agent:
    return Agent(
        client=create_chat_client(),
        name="LabAgent",
        instructions=(
            "You are a concise assistant for developers learning the Microsoft "
            "Agent Framework. Answer clearly and keep responses short."
        ),
    )


async def ask(agent: Agent, prompt: str) -> str:
    result = await agent.run(prompt)
    return result.text


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
