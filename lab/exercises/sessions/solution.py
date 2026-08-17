"""
Exercise 4 — Sessions (solution).

Run (two separate processes, same session id):

    uv run python -m exercises.sessions.solution "my name is Sam, remember it"
    uv run python -m exercises.sessions.solution "what did I say my name was?"
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

from agent_framework import Agent, AgentSession, FileSessionStore

from providers import create_chat_client

STORAGE_DIR = Path(__file__).resolve().parent / ".sessions"
SESSION_ID = "lab-sessions-exercise"


def create_agent() -> Agent:
    return Agent(
        client=create_chat_client(),
        name="SessionAgent",
        instructions="You are a helpful assistant. Keep answers short.",
    )


def create_store() -> FileSessionStore:
    STORAGE_DIR.mkdir(parents=True, exist_ok=True)
    return FileSessionStore(storage_path=STORAGE_DIR)


async def resume_or_create(agent: Agent, store: FileSessionStore, session_id: str) -> AgentSession:
    existing = await store.get(session_id)
    if existing is not None:
        return existing
    return agent.create_session(session_id=session_id)


async def save(store: FileSessionStore, session: AgentSession) -> None:
    await store.set(session.session_id, session)


async def main(prompt: str) -> None:
    agent = create_agent()
    store = create_store()
    session = await resume_or_create(agent, store, SESSION_ID)

    result = await agent.run(prompt, session=session)
    print(result.text)

    await save(store, session)


if __name__ == "__main__":
    from config import ConfigError

    question = " ".join(sys.argv[1:]) or "What did I just ask you?"
    try:
        asyncio.run(main(question))
    except ConfigError as error:
        sys.exit(f"\n{error}")
