"""
Module 5 - Test MCP Integration with OpsAgent

Run:
    python test_mcp_integration.py
    or
    uv run test_mcp_integration.py
"""

import asyncio
import os

from dotenv import load_dotenv
from openai import AsyncOpenAI

from agent_framework import Agent, MCPStreamableHTTPTool
from agent_framework.openai import OpenAIChatCompletionClient

load_dotenv()

github_base_url = "https://models.github.ai/inference"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_MODEL = os.getenv("GITHUB_MODEL")

if not GITHUB_TOKEN or not GITHUB_MODEL:
    raise ValueError("GITHUB_TOKEN and GITHUB_MODEL must be set in the .env file")


async def main():
    """Create and run OpsAgent with a hosted Microsoft Learn MCP tool."""

    print("🤖 OpsAgent (MCP) is ready for one question.\n")

    try:
        query = input("👤 You: ").strip()
    except (EOFError, KeyboardInterrupt):
        print("\n👋 Goodbye!")
        return

    if not query:
        print("No query provided. Exiting.")
        return

    async_openai = AsyncOpenAI(
        api_key=GITHUB_TOKEN,
        base_url=github_base_url,
    )

    client = OpenAIChatCompletionClient(
        model=GITHUB_MODEL,
        async_client=async_openai,
    )

    # MCP-only setup: no local Python function tools are added.
    learn_mcp = MCPStreamableHTTPTool(
        name="Microsoft Learn MCP",
        url="https://learn.microsoft.com/api/mcp",
        approval_mode="never_require",
    )

    async with Agent(
        client=client,
        name="OpsAgent",
        description="OpsAgent is an AI-powered operations and engineering assistant.",
        instructions=(
            "You are OpsAgent, an AI-powered operations and engineering assistant. "
            "Answer using Microsoft Learn MCP results only, with concise, actionable guidance for cloud operations."
        ),
        tools=[learn_mcp],
    ) as agent:
        result = await agent.run(query)
        print(f"\n💬 OpsAgent: {result.text}\n")


if __name__ == "__main__":
    asyncio.run(main())
