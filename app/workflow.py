"""
The triage workflow — deterministic steps around a non-deterministic one.

    triage_input  →  OpsAgent  →  capture_output

Workflows are the second pillar of Agent Framework, and the reason is visible in
those three boxes: the first and last are plain Python that behaves the same way
every time, and only the middle one calls a model. Severity classification is a
keyword match, so it does not need a model, cannot hallucinate a severity, and
costs nothing.

Reach for a workflow when the *shape* of the work is known in advance and only
the reasoning inside a step is not. When even the shape is unknown, that is what
the Harness in `harness.py` is for.
"""

from __future__ import annotations

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

CRITICAL = "CRITICAL"
HIGH = "HIGH"
INFO = "INFO"

_CRITICAL_KEYWORDS = ("critical", "down", "outage", "crash", "failed", "p1")
_HIGH_KEYWORDS = ("error", "high", "warn", "slow", "alert", "spike", "degraded")

TRIAGE_AGENT_NAME = "OpsTriage"

TRIAGE_INSTRUCTIONS = (
    "You are OpsAgent handling a triaged operations query. "
    "The query arrives tagged as [CRITICAL], [HIGH] or [INFO]. "
    "Match your urgency to the tag: CRITICAL means lead with the immediate "
    "mitigation, INFO means a calm explanation is fine. "
    "Give concise, actionable resolution steps."
)


def classify_severity(query: str) -> str:
    """
    Label a query CRITICAL, HIGH or INFO.

    A keyword match, not a model call — deliberately. Routing is the one
    decision in this pipeline that has to be reproducible, and asking an LLM to
    pick a severity makes it neither cheaper nor more reliable.
    """
    lowered = query.lower()
    if any(word in lowered for word in _CRITICAL_KEYWORDS):
        return CRITICAL
    if any(word in lowered for word in _HIGH_KEYWORDS):
        return HIGH
    return INFO


@executor(id="triage_input")
async def triage_input(query: str, ctx: WorkflowContext[str]) -> None:
    """Step 1 — tag the query with a severity and pass it on."""
    await ctx.send_message(f"[{classify_severity(query)}] {query}")


@executor(id="capture_output")
async def capture_output(response: AgentExecutorResponse, ctx: WorkflowContext[None, str]) -> None:
    """Step 3 — take the agent's text and yield it as the workflow's output."""
    await ctx.yield_output(response.agent_response.text)


def build_triage_workflow(client: Any | None = None) -> Workflow:
    """
    Build the triage workflow. Each call returns a fresh instance.

    Args:
        client: A chat client. Defaults to whatever `LLM_PROVIDER` selects, so
            the workflow swaps providers exactly like the agent does.
    """
    triage_agent = Agent(
        client=client or create_chat_client(),
        name=TRIAGE_AGENT_NAME,
        description="Handles severity-tagged operations queries.",
        instructions=TRIAGE_INSTRUCTIONS,
    )

    return (
        WorkflowBuilder(start_executor=triage_input, output_from=[capture_output])
        .add_edge(triage_input, triage_agent)
        .add_edge(triage_agent, capture_output)
        .build()
    )
