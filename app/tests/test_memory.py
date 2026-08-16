"""
Sessions and memory tests.

The claim under test is the one v1.0 made on slides and never shipped: that a
conversation actually survives the process. Every test here writes to a tmp
directory, so the assertion is about real files, not a mock.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from agent_framework import (
    AgentSession,
    FileHistoryProvider,
    FileSessionStore,
    InMemoryHistoryProvider,
)
from memory import (
    UserMemoryProvider,
    create_history_provider,
    create_session_store,
    resume_session,
    save_session,
)


class FakeAgent:
    """Just enough agent for the session helpers — they only call create_session."""

    def create_session(self, session_id: str | None = None) -> AgentSession:
        return AgentSession(session_id=session_id)


# ---------------------------------------------------------------------------
# Factories
# ---------------------------------------------------------------------------


def test_file_storage_is_the_default_shape(tmp_path: Path):
    assert isinstance(create_history_provider(tmp_path), FileHistoryProvider)
    assert isinstance(create_session_store(tmp_path), FileSessionStore)


def test_none_means_in_memory():
    """`storage_dir=None` is the escape hatch for tests and ephemeral hosts."""
    assert isinstance(create_history_provider(None), InMemoryHistoryProvider)
    assert create_session_store(None) is None


def test_factories_create_their_directories(tmp_path: Path):
    """A fresh clone has no .sessions/, so the factories must not assume one."""
    target = tmp_path / "does-not-exist-yet"

    create_history_provider(target)
    create_session_store(target)

    assert target.is_dir()
    assert {p.name for p in target.iterdir()} == {"history", "state"}


def test_history_and_sessions_do_not_share_a_directory(tmp_path: Path):
    """Transcripts and session state are different data with different shapes."""
    create_history_provider(tmp_path)
    create_session_store(tmp_path)

    assert (tmp_path / "history").is_dir()
    assert (tmp_path / "state").is_dir()


# ---------------------------------------------------------------------------
# Persistence
# ---------------------------------------------------------------------------


async def test_session_survives_a_new_store(tmp_path: Path):
    """
    The actual multi-turn promise.

    A second store object over the same directory stands in for a restarted
    process: nothing is shared but the files on disk.
    """
    agent = FakeAgent()
    store = create_session_store(tmp_path)

    session = await resume_session(agent, store, "conversation-1")
    session.state["user_name"] = "Sam"
    await save_session(store, session)

    reopened = create_session_store(tmp_path)
    resumed = await resume_session(agent, reopened, "conversation-1")

    assert resumed.session_id == "conversation-1"
    assert resumed.state["user_name"] == "Sam"


async def test_resume_starts_a_new_session_when_none_is_saved(tmp_path: Path):
    resumed = await resume_session(FakeAgent(), create_session_store(tmp_path), "brand-new")

    assert resumed.session_id == "brand-new"
    assert not resumed.state


async def test_sessions_are_isolated_by_id(tmp_path: Path):
    """Two users must not read each other's conversation."""
    agent, store = FakeAgent(), create_session_store(tmp_path)

    first = await resume_session(agent, store, "user-a")
    first.state["user_name"] = "Ada"
    await save_session(store, first)

    second = await resume_session(agent, store, "user-b")

    assert not second.state


async def test_saving_without_a_store_is_a_no_op():
    """In-memory mode must not need a different call site."""
    session = AgentSession(session_id="x")
    await save_session(None, session)  # must not raise

    resumed = await resume_session(FakeAgent(), None, "x")
    assert resumed.session_id == "x"


# ---------------------------------------------------------------------------
# UserMemoryProvider
# ---------------------------------------------------------------------------


class FakeContext:
    """Captures injected instructions and replays a fixed set of messages."""

    def __init__(self, texts: list[str] | None = None) -> None:
        self.instructions: list[str] = []
        self._messages = [type("Msg", (), {"text": t})() for t in (texts or [])]

    def extend_instructions(self, source_id: str, instructions: str) -> None:
        self.instructions.append(instructions)

    def get_messages(self, **kwargs: object) -> list[object]:
        return self._messages


async def _remember(texts: list[str]) -> dict:
    """Run one turn through the provider and return the resulting state."""
    provider, state = UserMemoryProvider(), {}
    context = FakeContext(texts)
    await provider.after_run(agent=None, session=None, context=context, state=state)
    return state


@pytest.mark.parametrize(
    ("said", "expected"),
    [
        ("my name is Sam", "Sam"),
        ("Hi, my name is dileepa and I need help", "Dileepa"),
        ("call me Ada", "Ada"),
        ("MY NAME IS Grace", "Grace"),
    ],
)
async def test_learns_a_name(said: str, expected: str):
    assert (await _remember([said]))["user_name"] == expected


@pytest.mark.parametrize(
    "said",
    [
        # The reason "I'm X" is not a supported phrasing: it would remember the
        # user as "getting" or "seeing", and a demo that misremembers in front
        # of a room is worse than one that remembers less.
        "I'm getting a 429 from Cosmos DB",
        "I am seeing timeouts",
        "the deployment failed again",
    ],
)
async def test_does_not_invent_a_name(said: str):
    assert await _remember([said]) == {}


async def test_first_name_wins():
    """A later message must not silently overwrite what we already know."""
    provider, state = UserMemoryProvider(), {"user_name": "Sam"}
    await provider.after_run(
        agent=None, session=None, context=FakeContext(["my name is Impostor"]), state=state
    )
    assert state["user_name"] == "Sam"


async def test_known_name_is_injected_as_instruction():
    provider = UserMemoryProvider()
    context = FakeContext()

    await provider.before_run(
        agent=None, session=None, context=context, state={"user_name": "Ada"}
    )

    assert any("Ada" in text for text in context.instructions)


async def test_unknown_name_still_injects_guidance():
    """The model needs to be told it doesn't know, or it will invent a name."""
    provider = UserMemoryProvider()
    context = FakeContext()

    await provider.before_run(agent=None, session=None, context=context, state={})

    assert context.instructions
    assert "not know" in context.instructions[0].lower()
