"""
Exercise 3 — MCP.

Goal: attach the hosted Microsoft Learn MCP server to an agent as a tool. See
README.md for the full brief.

Run:

    uv run python -m exercises.mcp.exercise "How do I configure health checks on Azure App Service?"

Then compare against solution.py.
"""

from __future__ import annotations

import asyncio
import sys

from agent_framework import Agent, MCPStreamableHTTPTool

from providers import create_chat_client

LEARN_MCP_URL = "https://learn.microsoft.com/api/mcp"


def create_learn_mcp() -> MCPStreamableHTTPTool:
    """
    TODO 1: build and return an `MCPStreamableHTTPTool` pointed at
    `LEARN_MCP_URL`. The server is read-only, so `approval_mode="never_require"`
    is appropriate here.
    """
    raise NotImplementedError("TODO 1: build the MCP tool")


def create_agent() -> Agent:
    """
    TODO 2: build and return an `Agent` with the Learn MCP tool attached via
    `tools=[create_learn_mcp()]`.
    """
    raise NotImplementedError("TODO 2: build the Agent with the MCP tool attached")


async def main(prompt: str) -> None:
    """
    TODO 3: open the agent as an async context manager and run `prompt`
    inside it, then print the answer text.

    Pattern:
        async with create_agent() as agent:
            result = await agent.run(prompt)
            print(result.text)

    The `async with` matters here: the MCP tool connects lazily on first use
    and needs to be closed again, which is what the context manager does.
    """
    raise NotImplementedError("TODO 3: run the agent inside `async with`")


if __name__ == "__main__":
    from config import ConfigError

    question = " ".join(sys.argv[1:]) or (
        "How do I configure health checks on Azure App Service?"
    )
    try:
        asyncio.run(main(question))
    except ConfigError as error:
        sys.exit(f"\n{error}")
