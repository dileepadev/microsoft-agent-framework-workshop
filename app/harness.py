"""
The Agent Harness — the pillar that did not exist when v1.0 was written.

`create_ops_agent` gives you an agent that answers a question. The Harness gives
you one that works through a *task*: it plans, tracks its own todo list,
compacts context when the conversation outgrows the window, keeps file-backed
memory, and asks before doing anything that needs approval.

It is not a different runtime. `create_harness_agent` returns an ordinary
`Agent`, composed from the same building blocks used elsewhere in this project,
so sessions, tools and context providers all work the same way.

    async with create_ops_harness() as agent:
        session = agent.create_session()
        result = await agent.run("Audit our deployment checklist and fix gaps.", session=session)

Use it when the shape of the work is unknown. When you already know the steps,
`workflow.py` is cheaper and reproducible.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from agent_framework import (
    Agent,
    AgentFileStore,
    FileSystemAgentFileStore,
    InMemoryAgentFileStore,
    create_harness_agent,
)

from mcp import create_learn_mcp
from memory import DEFAULT_STORAGE_DIR, create_history_provider
from providers import create_chat_client
from tools import OPSAGENT_TOOLS

HARNESS_NAME = "OpsAgentHarness"

#: Subdirectory of `storage_dir` holding the Harness's own file memory.
_FILE_MEMORY_SUBDIR = "harness-memory"

HARNESS_INSTRUCTIONS = (
    "You are working through operations tasks that take several steps. "
    "Plan before acting, keep your todo list current, and verify each step "
    "before moving on. Say plainly when a tool returns simulated data. "
    "Prefer the Microsoft Learn tools over recalling documentation from memory."
)

AGENT_INSTRUCTIONS = (
    "You are OpsAgent, an AI-powered operations and engineering assistant "
    "helping developers and cloud engineers troubleshoot, deploy and automate."
)


def create_ops_harness(
    client: Any | None = None,
    *,
    tools: list[Any] | None = None,
    storage_dir: Path | str | None = DEFAULT_STORAGE_DIR,
    with_mcp: bool = True,
    with_web_search: bool = False,
    max_context_window_tokens: int | None = None,
) -> Agent:
    """
    Build OpsAgent as a harness agent.

    Args:
        client: Defaults to whatever `LLM_PROVIDER` selects.
        tools: Overrides the default tool set.
        storage_dir: Where history is persisted, or None for in-memory.
        with_mcp: Attach the Microsoft Learn MCP server.
        with_web_search: Off by default, unlike the framework's own default.
            The Harness adds hosted web search only where the chosen client
            supports it — so leaving it on would make the demo behave one way on
            Gemini and another on Ollama, which is the opposite of the point
            this workshop is making. Turn it on when you have picked a provider.
        max_context_window_tokens: Enables compaction once set. Left unset by
            default because the right value is per-model, and guessing it here
            would be the same mistake as hardcoding a model name.

    Raises:
        ConfigError: The provider is unknown, unconfigured, or not installed.
    """
    # Resolve the provider before anything touches disk — see create_ops_agent.
    resolved_client = client or create_chat_client()

    # Pin file memory to storage_dir. Left alone, the Harness roots it at
    # `Path.cwd() / "agent-file-memory"`, so it would land wherever the command
    # happened to be run from — a different directory for every participant,
    # and one more stray folder in the repo.
    file_memory: AgentFileStore = (
        InMemoryAgentFileStore()
        if storage_dir is None
        else FileSystemAgentFileStore(root_directory=Path(storage_dir) / _FILE_MEMORY_SUBDIR)
    )

    harness_tools: list[Any] = list(OPSAGENT_TOOLS if tools is None else tools)
    if with_mcp:
        harness_tools.append(create_learn_mcp())

    return create_harness_agent(
        client=resolved_client,
        name=HARNESS_NAME,
        harness_instructions=HARNESS_INSTRUCTIONS,
        agent_instructions=AGENT_INSTRUCTIONS,
        tools=harness_tools,
        history_provider=create_history_provider(storage_dir),
        file_memory_store=file_memory,
        max_context_window_tokens=max_context_window_tokens,
        disable_web_search=not with_web_search,
    )
