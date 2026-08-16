"""
Agent Harness tests.

The Harness brings its own defaults, and two of them matter enough to pin here:
web search is off (it is provider-dependent, and this workshop is about code that
behaves the same everywhere) and compaction stays off until a token budget is
given (guessing one is the same mistake as hardcoding a model name).
"""

from __future__ import annotations

from pathlib import Path

from agent_framework import Agent

from config import Settings
from harness import HARNESS_NAME, create_ops_harness
from providers import create_chat_client
from tools import OPSAGENT_TOOLS


def _client():
    return create_chat_client(Settings("openai", api_key="fake", model="gpt-4o-mini"))


def test_harness_is_an_ordinary_agent():
    """
    The headline fact about the Harness: it is not a separate runtime.

    Same `Agent` type, so sessions, tools and context providers all still apply.
    """
    harness = create_ops_harness(_client(), storage_dir=None)

    assert isinstance(harness, Agent)
    assert harness.name == HARNESS_NAME
    assert hasattr(harness, "create_session")


def test_harness_carries_the_ops_tools_and_mcp():
    harness = create_ops_harness(_client(), storage_dir=None)

    tool_names = [tool.name for tool in harness.default_options["tools"]]
    for tool in OPSAGENT_TOOLS:
        assert tool.name in tool_names

    # MCP tools are kept separately by the framework, not in default_options.
    assert [tool.name for tool in harness.mcp_tools] == ["Microsoft Learn MCP"]


def test_mcp_can_be_left_off():
    assert create_ops_harness(_client(), storage_dir=None, with_mcp=False).mcp_tools == []


def test_web_search_is_off_by_default():
    """
    Deliberately different from the framework default.

    The Harness adds hosted web search only where the client supports it, which
    would make the same code behave one way on Gemini and another on Ollama —
    the opposite of what this workshop is demonstrating.
    """
    harness = create_ops_harness(_client(), storage_dir=None)
    tool_names = {tool.name for tool in harness.default_options["tools"]}

    assert not any("search" in name.lower() for name in tool_names)


def test_harness_uses_the_requested_storage(tmp_path: Path):
    """File memory is a Harness selling point, so it must honour storage_dir."""
    create_ops_harness(_client(), storage_dir=tmp_path)
    assert (tmp_path / "history").is_dir()


def test_file_memory_never_lands_in_the_working_directory(tmp_path: Path, monkeypatch):
    """
    Left to itself the Harness roots file memory at `cwd / "agent-file-memory"`.

    That would put it wherever the participant happened to run the command, so
    the factory pins it under storage_dir instead. This test runs from a clean
    cwd and asserts nothing appears there.
    """
    workdir = tmp_path / "cwd"
    workdir.mkdir()
    monkeypatch.chdir(workdir)

    create_ops_harness(_client(), storage_dir=tmp_path / "state")

    # The store creates its root lazily on first write, so what is checked here
    # is the absence of the cwd-rooted default rather than a directory existing.
    assert list(workdir.iterdir()) == []
    assert not (workdir / "agent-file-memory").exists()


def test_in_memory_storage_touches_no_disk(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    create_ops_harness(_client(), storage_dir=None)

    assert list(tmp_path.iterdir()) == []


def test_harness_respects_the_provider_factory(monkeypatch):
    """Same swap story as the plain agent — nothing here names a vendor."""
    monkeypatch.setenv("LLM_PROVIDER", "openai")
    monkeypatch.setenv("LLM_API_KEY", "fake")
    monkeypatch.setenv("LLM_MODEL", "gpt-4o-mini")

    harness = create_ops_harness(storage_dir=None)
    assert type(harness.client).__name__ == "OpenAIChatClient"
