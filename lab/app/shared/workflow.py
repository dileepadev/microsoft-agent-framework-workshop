"""
Workflow executors and builder — Module 8.

Implements the three-step ops triage pipeline:

    triage_input  →  OpsAgent  →  capture_output
"""

from agent_framework import (
    Agent,
    AgentExecutorResponse,
    WorkflowBuilder,
    WorkflowContext,
    executor,
)
from agent_framework.openai import OpenAIChatCompletionClient

# ---------------------------------------------------------------------------
# Severity classification
# ---------------------------------------------------------------------------

_CRITICAL_KEYWORDS = ("critical", "down", "outage", "crash", "failed")
_HIGH_KEYWORDS = ("error", "high", "warn", "slow", "alert", "spike")

OPSAGENT_NAME = "OpsAgent"
OPSAGENT_DESCRIPTION = "OpsAgent is an AI-powered operations and engineering assistant."


def classify_severity(query: str) -> str:
    """Return a severity label (CRITICAL / HIGH / INFO) for the given query."""
    lower = query.lower()
    if any(k in lower for k in _CRITICAL_KEYWORDS):
        return "CRITICAL"
    if any(k in lower for k in _HIGH_KEYWORDS):
        return "HIGH"
    return "INFO"


# ---------------------------------------------------------------------------
# Workflow executors
# ---------------------------------------------------------------------------


@executor(id="triage_input")
async def triage_input(query: str, ctx: WorkflowContext[str]) -> None:
    """Step 1: Tag the query with a severity label and pass it to OpsAgent."""
    severity = classify_severity(query)
    tagged = f"[{severity}] {query}"
    await ctx.send_message(tagged)


@executor(id="capture_output")
async def capture_output(
    response: AgentExecutorResponse, ctx: WorkflowContext[None, str]
) -> None:
    """Step 3: Extract the OpsAgent response text and yield it as workflow output."""
    await ctx.yield_output(response.agent_response.text)


# ---------------------------------------------------------------------------
# Workflow builder
# ---------------------------------------------------------------------------


def build_triage_workflow(client: OpenAIChatCompletionClient):
    """
    Build the 3-step triage workflow (Module 8):

        triage_input  →  OpsAgent  →  capture_output

    Each call creates a fresh workflow instance.
    """
    workflow_agent = Agent(
        client=client,
        name=OPSAGENT_NAME,
        description=OPSAGENT_DESCRIPTION,
        instructions=(
            "You are OpsAgent, an AI-powered operations and engineering assistant. "
            "You receive tagged ops queries in the format [SEVERITY] description. "
            "Provide concise, actionable resolution steps. Keep responses short and practical."
        ),
    )
    return (
        WorkflowBuilder(
            start_executor=triage_input,
            output_from=[capture_output],
        )
        .add_edge(triage_input, workflow_agent)
        .add_edge(workflow_agent, capture_output)
        .build()
    )
