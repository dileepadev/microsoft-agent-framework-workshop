"""
Module 7 - Test Memory & Persistence with OpsAgent

Run:
    python test_memory_persistence.py
    or
    uv run test_memory_persistence.py
"""

import asyncio
import os
from typing import Any

from dotenv import load_dotenv
from openai import AsyncOpenAI

from agent_framework import (
    Agent,
    AgentSession,
    ContextProvider,
    InMemoryHistoryProvider,
    SessionContext,
)
from agent_framework.openai import OpenAIChatCompletionClient

load_dotenv()

github_base_url = "https://models.github.ai/inference"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_MODEL = os.getenv("GITHUB_MODEL")

if not GITHUB_TOKEN or not GITHUB_MODEL:
    raise ValueError("GITHUB_TOKEN and GITHUB_MODEL must be set in the .env file")


# ---------------------------------------------------------------------------
# Custom Context Provider
# ---------------------------------------------------------------------------


class UserMemoryProvider(ContextProvider):
    """Remembers user info in session state and injects personalization instructions."""

    DEFAULT_SOURCE_ID = "user_memory"

    def __init__(self):
        super().__init__(self.DEFAULT_SOURCE_ID)

    async def before_run(
        self,
        *,
        agent: Any,
        session: AgentSession,
        context: SessionContext,
        state: dict[str, Any],
    ) -> None:
        """Inject personalization instructions based on stored user info."""
        user_name = state.get("user_name")
        if user_name:
            context.extend_instructions(
                self.source_id,
                f"The user's name is {user_name}. Always address them by name.",
            )
        else:
            context.extend_instructions(
                self.source_id,
                "You don't know the user's name yet. Ask for it politely.",
            )

    async def after_run(
        self,
        *,
        agent: Any,
        session: AgentSession,
        context: SessionContext,
        state: dict[str, Any],
    ) -> None:
        """Extract and store user info in session state after each call."""
        for msg in context.get_messages():
            text = msg.text if hasattr(msg, "text") else ""
            if isinstance(text, str) and "my name is" in text.lower():
                name = (
                    text.lower()
                    .split("my name is")[-1]
                    .strip()
                    .split()[0]
                    .strip(".,!?;:")
                    .capitalize()
                )
                state["user_name"] = name


# ---------------------------------------------------------------------------
# Agent setup and test runner
# ---------------------------------------------------------------------------


async def main():
    """Create and run OpsAgent with memory and persistence via context providers."""

    print("🤖 OpsAgent (Memory) is ready.")
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
            "Keep responses concise, actionable, and practical."
        ),
        context_providers=[
            UserMemoryProvider(),
            # InMemoryHistoryProvider persists conversation history across turns.
            # Only one history provider should have load_messages=True.
            InMemoryHistoryProvider(load_messages=True),
        ],
    )

    session = agent.create_session()

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
            # Show what UserMemoryProvider stored in session state.
            provider_state = session.state.get("user_memory", {})
            stored_name = provider_state.get("user_name")
            if stored_name:
                print(f"\n📦 Session State: Stored user name → {stored_name}")
            print("👋 Goodbye!")
            break

        result = await agent.run(query, session=session)
        print(f"💬 OpsAgent: {result.text}\n")


if __name__ == "__main__":
    asyncio.run(main())
