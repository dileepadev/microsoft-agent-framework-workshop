"""
Module 3 - Test Microsoft Agent Framework Agent

Run:
    python test_microsoft_agent_framework.py
    or
    uv run test_microsoft_agent_framework.py
"""

import asyncio
import os

from dotenv import load_dotenv
from openai import AsyncOpenAI

from agent_framework import Agent
from agent_framework.openai import OpenAIChatCompletionClient

load_dotenv()

github_base_url = "https://models.github.ai/inference"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_MODEL = os.getenv("GITHUB_MODEL")

if not GITHUB_TOKEN or not GITHUB_MODEL:
    raise ValueError("GITHUB_TOKEN and GITHUB_MODEL must be set in the .env file")


async def run_agent_non_streaming(agent: Agent, query: str):
    """Run the agent in non-streaming mode."""
    print("🧪 Running non-streaming test...")
    result = await agent.run(query)
    print(f"💬 OpsAgent: {result}")
    print("\n✅ Non-streaming test complete\n")


async def run_agent_streaming(agent: Agent, query: str):
    """Run the agent in streaming mode."""
    print("🧪 Running streaming test...")
    print("💬 OpsAgent: ", end="", flush=True)

    async for chunk in agent.run(query, stream=True):
        if chunk.text:
            print(chunk.text, end="", flush=True)

    print("\n✅ Streaming test complete\n")


async def main():
    """Create and run OpsAgent with GitHub Models."""

    print("🤖 Initializing OpsAgent...")

    async_openai = AsyncOpenAI(
        api_key=GITHUB_TOKEN,
        base_url=github_base_url,
    )

    client = OpenAIChatCompletionClient(
        model=GITHUB_MODEL,
        async_client=async_openai,
    )

    agent = Agent(
        client=client,
        name="OpsAgent",
        description="OpsAgent is an AI-powered operations and engineering assistant.",
        instructions="""
        You are OpsAgent, an AI-powered operations and engineering assistant.
        Help developers and cloud engineers troubleshoot issues,
        retrieve documentation, analyze systems, and automate operational workflows.
        Keep responses concise, actionable, and practical.
        """,
    )

    await run_agent_non_streaming(agent, "How do I deploy a container app in Azure?")

    # Wait a moment before starting the streaming test to ensure clear separation in the output
    print("⏳ Waiting 5 seconds before starting streaming test...\n")
    await asyncio.sleep(5)

    await run_agent_streaming(agent, "How do I deploy a container app in Azure?")


if __name__ == "__main__":
    asyncio.run(main())
