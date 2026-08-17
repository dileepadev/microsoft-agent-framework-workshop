"""
Exercise 2 — Tools.

Goal: write a custom @tool function and attach it to an agent. See README.md
for the full brief.

Run:

    uv run python -m exercises.tools.exercise "What's the monthly cost of a VM at $0.05/hour running 24 hours a day?"

Then compare against solution.py.
"""

from __future__ import annotations

import asyncio
import sys
from typing import Annotated

from agent_framework import Agent, tool
from pydantic import Field

from providers import create_chat_client

# TODO 1: decorate this function with @tool(approval_mode="never_require"),
# annotate hourly_rate and hours_per_day with Annotated[..., Field(description=...)],
# give hours_per_day a default of 24, and return a formatted string such as
# "At $0.05/hour for 24h/day, the estimated monthly cost is $36.00."
def estimate_monthly_cost(hourly_rate: float, hours_per_day: float = 24) -> str:
    """Estimate the monthly cost of a resource billed by the hour."""
    raise NotImplementedError("TODO 1: implement and decorate this tool")


def create_agent() -> Agent:
    """
    TODO 2: build and return an `Agent` with `estimate_monthly_cost` attached
    via `tools=[...]`.
    """
    raise NotImplementedError("TODO 2: build the Agent with the tool attached")


async def ask(agent: Agent, prompt: str) -> str:
    result = await agent.run(prompt)
    return result.text


async def main(prompt: str) -> None:
    agent = create_agent()
    print(await ask(agent, prompt))


if __name__ == "__main__":
    from config import ConfigError

    question = " ".join(sys.argv[1:]) or (
        "What's the monthly cost of a VM at $0.05/hour running 24 hours a day?"
    )
    try:
        asyncio.run(main(question))
    except ConfigError as error:
        sys.exit(f"\n{error}")
