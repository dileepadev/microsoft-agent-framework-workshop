"""
Exercise 2 — Tools (solution).

Run:

    uv run python -m exercises.tools.solution "What's the monthly cost of a VM at $0.05/hour running 24 hours a day?"
"""

from __future__ import annotations

import asyncio
import sys
from typing import Annotated

from agent_framework import Agent, tool
from pydantic import Field

from providers import create_chat_client

DAYS_PER_MONTH = 30


@tool(approval_mode="never_require")
def estimate_monthly_cost(
    hourly_rate: Annotated[
        float,
        Field(description="The resource's hourly billing rate in USD, e.g. 0.05."),
    ],
    hours_per_day: Annotated[
        float,
        Field(description="How many hours a day the resource runs."),
    ] = 24,
) -> str:
    """Estimate the monthly cost of a resource billed by the hour."""
    monthly = hourly_rate * hours_per_day * DAYS_PER_MONTH
    return (
        f"At ${hourly_rate:.2f}/hour for {hours_per_day:g}h/day, the estimated "
        f"monthly cost is ${monthly:.2f} ({DAYS_PER_MONTH}-day month)."
    )


def create_agent() -> Agent:
    return Agent(
        client=create_chat_client(),
        name="CostAgent",
        instructions=(
            "You help engineers estimate cloud spend. Use the "
            "estimate_monthly_cost tool for any cost calculation rather than "
            "doing the arithmetic yourself."
        ),
        tools=[estimate_monthly_cost],
    )


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
