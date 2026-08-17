"""
Exercise 4 — Sessions.

Goal: make a conversation survive a restart. See README.md for the full
brief.

Run (two separate processes, same session id):

    uv run python -m exercises.sessions.exercise "my name is Sam, remember it"
    uv run python -m exercises.sessions.exercise "what did I say my name was?"

Then compare against solution.py.
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

from agent_framework import Agent, AgentSession, FileSessionStore

from providers import create_chat_client

#: Gitignored — transcripts are user data, same reasoning as app/.sessions/.
STORAGE_DIR = Path(__file__).resolve().parent / ".sessions"
SESSION_ID = "lab-sessions-exercise"


def create_agent() -> Agent:
    return Agent(
        client=create_chat_client(),
        name="SessionAgent",
        instructions="You are a helpful assistant. Keep answers short.",
    )


def create_store() -> FileSessionStore:
    """
    TODO 1: build and return a `FileSessionStore` rooted at `STORAGE_DIR`.

    Create `STORAGE_DIR` first if it doesn't exist yet (`Path.mkdir` with
    `parents=True, exist_ok=True`).
    """
    raise NotImplementedError("TODO 1: build the session store")


async def resume_or_create(agent: Agent, store: FileSessionStore, session_id: str) -> AgentSession:
    """
    TODO 2: look up `session_id` in `store` with `await store.get(session_id)`.

    If it returns a session, return that. If it returns None, start a new one
    with `agent.create_session(session_id=session_id)` and return that
    instead.
    """
    raise NotImplementedError("TODO 2: resume or create the session")


async def save(store: FileSessionStore, session: AgentSession) -> None:
    """
    TODO 3: persist `session`'s state back to `store` with
    `await store.set(session.session_id, session)`.
    """
    raise NotImplementedError("TODO 3: save the session")


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
