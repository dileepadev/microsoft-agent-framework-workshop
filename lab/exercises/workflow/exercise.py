"""
Exercise 6 — Workflow.

Goal: build a three-step WorkflowBuilder pipeline — tag_input -> SupportAgent
-> capture_output. See README.md for the full brief.

Run:

    uv run python -m exercises.workflow.exercise "I was charged twice for my subscription this month"

Then compare against solution.py.
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
    """
    TODO 1: return BILLING if any word in _BILLING_KEYWORDS appears in
    `message` (case-insensitive), TECHNICAL if any word in
    _TECHNICAL_KEYWORDS appears, otherwise GENERAL. Check billing before
    technical, so a message matching both reads as the more specific topic.
    """
    raise NotImplementedError("TODO 1: classify the message topic")


@executor(id="tag_input")
async def tag_input(message: str, ctx: WorkflowContext[str]) -> None:
    """
    TODO 2: tag `message` with its topic and send it on, e.g.
    `await ctx.send_message(f"[{classify_topic(message)}] {message}")`.
    """
    raise NotImplementedError("TODO 2: tag and forward the message")


@executor(id="capture_output")
async def capture_output(response: AgentExecutorResponse, ctx: WorkflowContext[None, str]) -> None:
    """
    TODO 3: yield the agent's answer as the workflow's output with
    `await ctx.yield_output(response.agent_response.text)`.
    """
    raise NotImplementedError("TODO 3: yield the agent's answer")


def build_support_workflow(client: Any | None = None) -> Workflow:
    """
    TODO 4: build the support `Agent` (name=SUPPORT_AGENT_NAME,
    instructions=SUPPORT_INSTRUCTIONS, client=client or create_chat_client())
    and wire `tag_input -> support_agent -> capture_output` with
    `WorkflowBuilder(start_executor=tag_input,
    output_from=[capture_output]).add_edge(...).add_edge(...).build()`.
    """
    raise NotImplementedError("TODO 4: build and wire the workflow")


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
