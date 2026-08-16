"""
Sessions and memory — what OpsAgent remembers, and where it actually keeps it.

Two different things, easy to confuse:

  **History** is the transcript. `HistoryProvider` replays previous turns into
  the next request, which is what makes a conversation multi-turn.

  **Memory** is a fact worth keeping *out* of the transcript — something learned
  once and injected as instruction on every later turn. `ContextProvider` does
  that, and `UserMemoryProvider` below is a small worked example.

Both are `ContextProvider`s, so both attach to an agent the same way.

## On persistence

v1.0 promised SQLite and Cosmos DB on the slides and shipped neither. This
module makes a smaller claim and keeps it: **history and session state are
written to JSON files on disk**, under `app/.sessions/` by default. Restart the
process, reload the session by id, and the conversation is still there.

That is genuinely persistent and genuinely modest. It is not a database, it does
not survive redeployment of an ephemeral host, and it does not shard. Swapping in
Redis, Cosmos or Mem0 means changing the two factories below and nothing else —
those integrations ship as separate `agent-framework-*` packages.

One more thing worth saying out loud: `FileHistoryProvider` and `FileSessionStore`
are both marked **experimental** by the framework and emit an `ExperimentalWarning`
on construction. They work, and they are the right shape for a workshop, but the
API may change. `InMemoryHistoryProvider` is not experimental.

Pass `storage_dir=None` for in-memory instead, which is what the tests use.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from agent_framework import (
    AgentSession,
    ContextProvider,
    FileHistoryProvider,
    FileSessionStore,
    HistoryProvider,
    InMemoryHistoryProvider,
    SessionContext,
    SessionStore,
)

#: Where conversations live. Gitignored — transcripts are user data.
DEFAULT_STORAGE_DIR = Path(__file__).resolve().parent / ".sessions"

_HISTORY_SUBDIR = "history"
_SESSIONS_SUBDIR = "state"


# ---------------------------------------------------------------------------
# Factories
# ---------------------------------------------------------------------------


def create_history_provider(storage_dir: Path | str | None = DEFAULT_STORAGE_DIR) -> HistoryProvider:
    """
    Build the conversation history provider.

    Args:
        storage_dir: Directory to persist transcripts under, or None for
            in-memory history that dies with the process.
    """
    if storage_dir is None:
        return InMemoryHistoryProvider(load_messages=True)

    path = Path(storage_dir) / _HISTORY_SUBDIR
    path.mkdir(parents=True, exist_ok=True)
    return FileHistoryProvider(storage_path=path, load_messages=True)


def create_session_store(storage_dir: Path | str | None = DEFAULT_STORAGE_DIR) -> SessionStore | None:
    """
    Build the session store, which persists a session's *state* by id.

    Returns None when `storage_dir` is None: with nothing to write to there is
    no store to hand back, and callers should treat sessions as ephemeral.

    The store is deliberately separate from the agent. Agent Framework does not
    take a store parameter — you save and load sessions yourself, which is what
    lets a web request pick a conversation back up by id.
    """
    if storage_dir is None:
        return None

    path = Path(storage_dir) / _SESSIONS_SUBDIR
    path.mkdir(parents=True, exist_ok=True)
    return FileSessionStore(storage_path=path)


async def resume_session(agent: Any, store: SessionStore | None, session_id: str) -> AgentSession:
    """
    Load a saved session by id, or start a new one under that id.

    This is the whole multi-turn story for a server: the client sends a session
    id, and the conversation continues where it left off even if the process
    restarted in between.
    """
    if store is not None:
        existing = await store.get(session_id)
        if existing is not None:
            return existing
    return agent.create_session(session_id=session_id)


async def save_session(store: SessionStore | None, session: AgentSession) -> None:
    """Persist a session's state. A no-op when running in-memory."""
    if store is not None:
        await store.set(session.session_id, session)


# ---------------------------------------------------------------------------
# Memory
# ---------------------------------------------------------------------------

#: Deliberately narrow. "my name is X" and "call me X" are unambiguous;
#: "I'm X" is not — it matches "I'm getting a 429" and would remember the user
#: as "getting". A demo that misremembers is worse than one that remembers less.
_NAME_PATTERN = re.compile(
    r"\b(?:my name is|call me)\s+([A-Za-z][A-Za-z'\-]{1,30})",
    re.IGNORECASE,
)


class UserMemoryProvider(ContextProvider):
    """
    Remembers the user's name across turns and addresses them by it.

    A small, honest example of the pattern rather than a real memory system:

      `before_run`  reads state and adds a personalisation instruction.
      `after_run`   scans new messages for a name and writes it to state.

    The `state` dict it writes to belongs to the session, so pairing this with
    `create_session_store` is what makes the name survive a restart. Without a
    store, it lasts only as long as the process.

    For production memory — semantic recall, summarisation, vector search — use
    a real provider. Agent Framework ships `MemoryContextProvider`, and Mem0 and
    Foundry memory integrations exist as separate packages.
    """

    DEFAULT_SOURCE_ID = "user_memory"

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
        """Inject what we know about the user ahead of the model call."""
        user_name = state.get("user_name")
        if user_name:
            context.extend_instructions(
                self.source_id,
                f"The user's name is {user_name}. Address them by name.",
            )
        else:
            context.extend_instructions(
                self.source_id,
                "You do not know the user's name yet. If it comes up naturally, ask.",
            )

    async def after_run(
        self,
        *,
        agent: Any,
        session: AgentSession,
        context: SessionContext,
        state: dict[str, Any],
    ) -> None:
        """Learn the user's name from this turn, if they offered it."""
        if state.get("user_name"):
            return

        for message in context.get_messages(include_input=True):
            text = getattr(message, "text", None)
            if not isinstance(text, str):
                continue
            match = _NAME_PATTERN.search(text)
            if match:
                state["user_name"] = match.group(1).strip("'-").capitalize()
                return
