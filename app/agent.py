"""
OpsAgent — the agent this workshop builds.

This module is the payoff of `providers.py`. Read it and notice what is absent:
no vendor name, no API key, no base URL, no model id. It asks the factory for a
chat client and describes the agent it wants. Swapping Gemini for Claude, or for
a model running on this laptop, changes `.env` and nothing here.

    from agent import create_ops_agent

    agent = create_ops_agent()
    result = await agent.run("Is Azure App Service healthy in West Europe?")

Later modules extend this same function with MCP, sessions, memory and
workflows. The shape does not change.

Try it directly:

    uv run python -m agent "What should I check before deploying a Container App?"
"""

from __future__ import annotations

from typing import Any

from agent_framework import Agent

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
) -> Agent:
    """
    Build OpsAgent.

    Args:
        client: A chat client. Defaults to whatever `LLM_PROVIDER` selects —
            which is the entire point, so pass this only in tests or when
            running two providers side by side.
        tools: Overrides the default tool set.
        instructions: Overrides the default system prompt.

    Raises:
        ConfigError: The provider is unknown, unconfigured, or its package is
            not installed. The message names what to fix.
    """
    return Agent(
        client=client or create_chat_client(),
        name=OPSAGENT_NAME,
        description=OPSAGENT_DESCRIPTION,
        instructions=instructions or OPSAGENT_INSTRUCTIONS,
        tools=list(OPSAGENT_TOOLS if tools is None else tools),
    )


async def _main(prompt: str) -> None:
    """Run one prompt against the configured provider and stream the answer."""
    from config import MODEL_VAR, PROVIDER_VAR, Settings

    settings = Settings.from_env()
    # flush so this banner cannot land after an error written to stderr.
    print(f"{PROVIDER_VAR}={settings.provider}  {MODEL_VAR}={settings.model}\n", flush=True)

    agent = create_ops_agent()
    print(f"You:      {prompt}")
    print("OpsAgent: ", end="", flush=True)
    async for chunk in agent.run(prompt, stream=True):
        if chunk.text:
            print(chunk.text, end="", flush=True)
    print()


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
