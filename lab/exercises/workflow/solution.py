"""
Exercise 6 — Workflow (solution).

Run:

    uv run python -m exercises.workflow.solution "I was charged twice for my subscription this month"
"""

from __future__ import annotations

import asyncio
import sys
from typing import Any

from agent_framework import (
    Agent,
    AgentExecutorResponse,
    Workflow,
    WorkflowBuilder,
    WorkflowContext,
    executor,
)

from providers import create_chat_client

BILLING = "BILLING"
TECHNICAL = "TECHNICAL"
GENERAL = "GENERAL"

_BILLING_KEYWORDS = ("invoice", "charge", "charged", "billing", "refund", "payment", "subscription")
_TECHNICAL_KEYWORDS = ("error", "bug", "crash", "broken", "not working", "fails", "500", "timeout")

SUPPORT_AGENT_NAME = "SupportAgent"

SUPPORT_INSTRUCTIONS = (
    "You are a support agent handling a tagged customer message. The message "
    "arrives prefixed with [BILLING], [TECHNICAL] or [GENERAL]. Match your "
    "tone and next steps to the tag. Keep the reply short and actionable."
)


def classify_topic(message: str) -> str:
    lowered = message.lower()
    if any(word in lowered for word in _BILLING_KEYWORDS):
        return BILLING
    if any(word in lowered for word in _TECHNICAL_KEYWORDS):
        return TECHNICAL
    return GENERAL


@executor(id="tag_input")
async def tag_input(message: str, ctx: WorkflowContext[str]) -> None:
    await ctx.send_message(f"[{classify_topic(message)}] {message}")


@executor(id="capture_output")
async def capture_output(response: AgentExecutorResponse, ctx: WorkflowContext[None, str]) -> None:
    await ctx.yield_output(response.agent_response.text)


def build_support_workflow(client: Any | None = None) -> Workflow:
    support_agent = Agent(
        client=client or create_chat_client(),
        name=SUPPORT_AGENT_NAME,
        description="Handles topic-tagged support messages.",
        instructions=SUPPORT_INSTRUCTIONS,
    )

    return (
        WorkflowBuilder(start_executor=tag_input, output_from=[capture_output])
        .add_edge(tag_input, support_agent)
        .add_edge(support_agent, capture_output)
        .build()
    )


async def main(message: str) -> None:
    workflow = build_support_workflow()
    events = await workflow.run(message)
    for output in events.get_outputs():
        print(output)


if __name__ == "__main__":
    from config import ConfigError

    text = " ".join(sys.argv[1:]) or "I was charged twice for my subscription this month"
    try:
        asyncio.run(main(text))
    except ConfigError as error:
        sys.exit(f"\n{error}")
