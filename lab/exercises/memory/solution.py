"""
Exercise 5 — Memory (solution).

Run:

    uv run python -m exercises.memory.solution
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
        count = state.get("count", 0)
        context.extend_instructions(
            self.source_id,
            f"This is question number {count + 1} from this user in this session. "
            "If it's the third or later, mention the question number in your answer.",
        )

    async def after_run(
        self,
        *,
        agent: Any,
        session: AgentSession,
        context: SessionContext,
        state: dict[str, Any],
    ) -> None:
        state["count"] = state.get("count", 0) + 1


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
