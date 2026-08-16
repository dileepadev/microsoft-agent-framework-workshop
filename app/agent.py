"""
OpsAgent — the agent this workshop builds.

This module is the payoff of `providers.py`. Read it and notice what is absent:
no vendor name, no API key, no base URL, no model id. It asks the factory for a
chat client and describes the agent it wants. Swapping Gemini for Claude, or for
a model running on this laptop, changes `.env` and nothing here.

    from agent import create_ops_agent

    async with create_ops_agent() as agent:
        session = agent.create_session()
        result = await agent.run("Is Azure App Service healthy?", session=session)

The `async with` matters once MCP is attached: the agent opens a connection to
the Microsoft Learn server on first use and needs to close it again.

Try it directly:

    uv run python -m agent "What should I check before deploying a Container App?"
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from agent_framework import Agent

from mcp import create_learn_mcp
from memory import DEFAULT_STORAGE_DIR, UserMemoryProvider, create_history_provider
from providers import create_chat_client
from tools import OPSAGENT_TOOLS

OPSAGENT_NAME = "OpsAgent"

OPSAGENT_DESCRIPTION = "An AI-powered operations and engineering assistant."

OPSAGENT_INSTRUCTIONS = (
    "You are OpsAgent, an AI-powered operations and engineering assistant. "
    "Help developers and cloud engineers troubleshoot issues, retrieve documentation, "
    "analyse systems and automate operational work. "
    "Use the available tools when they are relevant, and say so when a tool returns "
    "simulated data rather than a live reading. "
    "Keep responses concise, actionable and practical."
)


def create_ops_agent(
    client: Any | None = None,
    *,
    tools: list[Any] | None = None,
    instructions: str | None = None,
    with_mcp: bool = True,
    with_memory: bool = True,
    storage_dir: Path | str | None = DEFAULT_STORAGE_DIR,
) -> Agent:
    """
    Build OpsAgent.

    Args:
        client: A chat client. Defaults to whatever `LLM_PROVIDER` selects —
            which is the entire point, so pass this only in tests or when
            running two providers side by side.
        tools: Overrides the default tool set.
        instructions: Overrides the default system prompt.
        with_mcp: Attach the Microsoft Learn MCP server.
        with_memory: Attach conversation history and the user-memory provider.
        storage_dir: Where history is persisted, or None to keep it in memory.

    Raises:
        ConfigError: The provider is unknown, unconfigured, or its package is
            not installed. The message names what to fix.
    """
    # Resolve the provider first. Building the history provider creates
    # directories, and a misconfigured agent should fail on the config error
    # rather than leave a storage directory behind on its way out.
    resolved_client = client or create_chat_client()

    agent_tools: list[Any] = list(OPSAGENT_TOOLS if tools is None else tools)
    if with_mcp:
        agent_tools.append(create_learn_mcp())

    # Order matters: UserMemoryProvider adds an instruction, the history
    # provider replays the transcript. Both run before every turn.
    context_providers: list[Any] = []
    if with_memory:
        context_providers = [UserMemoryProvider(), create_history_provider(storage_dir)]

    return Agent(
        client=resolved_client,
        name=OPSAGENT_NAME,
        description=OPSAGENT_DESCRIPTION,
        instructions=instructions or OPSAGENT_INSTRUCTIONS,
        tools=agent_tools,
        context_providers=context_providers,
    )


#: The CLI reuses one session id so persistence is demonstrable in two commands:
#:
#:     uv run python -m agent "my name is Sam, and our API is returning 429s"
#:     uv run python -m agent "what did I say my name was?"
#:
#: The second process has no memory of the first except what is on disk.
CLI_SESSION_ID = "cli"


async def _main(prompt: str) -> None:
    """Run one prompt against the configured provider and stream the answer."""
    from config import MODEL_VAR, PROVIDER_VAR, Settings
    from memory import create_session_store, resume_session, save_session

    settings = Settings.from_env()
    # flush so this banner cannot land after an error written to stderr.
    print(f"{PROVIDER_VAR}={settings.provider}  {MODEL_VAR}={settings.model}\n", flush=True)

    store = create_session_store()
    async with create_ops_agent() as agent:
        session = await resume_session(agent, store, CLI_SESSION_ID)

        print(f"You:      {prompt}")
        print("OpsAgent: ", end="", flush=True)
        async for chunk in agent.run(prompt, stream=True, session=session):
            if chunk.text:
                print(chunk.text, end="", flush=True)
        print()

        await save_session(store, session)


if __name__ == "__main__":
    import asyncio
    import sys

    from config import ConfigError

    question = " ".join(sys.argv[1:]) or "Is Azure App Service healthy in West Europe?"
    try:
        asyncio.run(_main(question))
    except ConfigError as error:
        # Configuration problems are expected and already explain themselves.
        # A traceback would only bury the sentence that helps.
        sys.exit(f"\n{error}")
