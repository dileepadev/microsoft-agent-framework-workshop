"""
Exercise 5 — Memory.

Goal: write a ContextProvider that tracks a fact across turns and injects it
as an instruction. See README.md for the full brief.

Run:

    uv run python -m exercises.memory.exercise

Then compare against solution.py.
"""

from __future__ import annotations

import asyncio
import sys
from typing import Any

from agent_framework import Agent, AgentSession, ContextProvider, SessionContext

from providers import create_chat_client


class QuestionCounterMemory(ContextProvider):
    """Remembers how many questions the user has asked this session."""

    DEFAULT_SOURCE_ID = "question_counter"

    def __init__(self, source_id: str = DEFAULT_SOURCE_ID) -> None:
        super().__init__(source_id)

    async def before_run(
        self,
        *,
        agent: Any,
        session: AgentSession,
        context: SessionContext,
        state: dict[str, Any],
    ) -> None:
        """
        TODO 1: read `state.get("count", 0)` and call
        `context.extend_instructions(self.source_id, text)` with an
        instruction naming which question number this is (the count plus
        one, since this turn hasn't been counted yet).
        """
        raise NotImplementedError("TODO 1: inject the question-count instruction")

    async def after_run(
        self,
        *,
        agent: Any,
        session: AgentSession,
        context: SessionContext,
        state: dict[str, Any],
    ) -> None:
        """
        TODO 2: increment `state["count"]` by one, defaulting to 0 if it
        isn't set yet.
        """
        raise NotImplementedError("TODO 2: increment the counter")


def create_agent() -> Agent:
    return Agent(
        client=create_chat_client(),
        name="MemoryAgent",
        instructions="You are a helpful assistant. Keep answers to one sentence.",
        context_providers=[QuestionCounterMemory()],
    )


async def main(prompts: list[str]) -> None:
    agent = create_agent()
    session = agent.create_session()

    for prompt in prompts:
        result = await agent.run(prompt, session=session)
        print(f"You:   {prompt}")
        print(f"Agent: {result.text}\n")


if __name__ == "__main__":
    from config import ConfigError

    questions = sys.argv[1:] or [
        "What is Azure App Service?",
        "And what about AKS?",
        "One more — what's a Function App?",
    ]
    try:
        asyncio.run(main(questions))
    except ConfigError as error:
        sys.exit(f"\n{error}")
