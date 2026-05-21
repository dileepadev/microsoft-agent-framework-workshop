"""
Module 2 - Test GitHub Models Connection

Run:
    python test_github_models_connection.py
    or
    uv run test_github_models_connection.py
"""

import asyncio
import os

from dotenv import load_dotenv
from openai import AsyncOpenAI

load_dotenv()


async def main():
    """Send a simple request to GitHub Models."""

    print("🔌 Connecting to GitHub Models...")

    client = AsyncOpenAI(
        api_key=os.getenv("GITHUB_TOKEN"),
        base_url="https://models.github.ai/inference",
    )

    print("📨 Sending request...")

    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": "Reply with: Hello from GitHub Models!",
            }
        ],
    )

    message = response.choices[0].message.content

    print("\n💬 Model Response:", message)


if __name__ == "__main__":
    asyncio.run(main())