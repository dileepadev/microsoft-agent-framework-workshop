"""
Exercise 3 — MCP (solution).

Run:

    uv run python -m exercises.mcp.solution "How do I configure health checks on Azure App Service?"
"""

from __future__ import annotations

import asyncio
import sys

from agent_framework import Agent, MCPStreamableHTTPTool

from providers import create_chat_client

LEARN_MCP_URL = "https://learn.microsoft.com/api/mcp"


def create_learn_mcp() -> MCPStreamableHTTPTool:
    return MCPStreamableHTTPTool(
        name="Microsoft Learn MCP",
        url=LEARN_MCP_URL,
        approval_mode="never_require",
    )


def create_agent() -> Agent:
    return Agent(
        client=create_chat_client(),
        name="LearnAgent",
        instructions=(
            "You answer questions about Azure and Microsoft technologies. "
            "Use the Microsoft Learn tools to ground your answer in real "
            "documentation rather than recalling it from memory."
        ),
        tools=[create_learn_mcp()],
    )


async def main(prompt: str) -> None:
    async with create_agent() as agent:
        result = await agent.run(prompt)
        print(result.text)


if __name__ == "__main__":
    from config import ConfigError

    question = " ".join(sys.argv[1:]) or (
        "How do I configure health checks on Azure App Service?"
    )
    try:
        asyncio.run(main(question))
    except ConfigError as error:
        sys.exit(f"\n{error}")
