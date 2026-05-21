"""
Module 8 - Test Workflows with OpsAgent

Run:
    python test_workflows.py
    or
    uv run test_workflows.py
"""

import asyncio
import os

from dotenv import load_dotenv
from openai import AsyncOpenAI

from agent_framework import (
    Agent,
    AgentExecutorResponse,
    WorkflowBuilder,
    WorkflowContext,
    executor,
)
from agent_framework.openai import OpenAIChatCompletionClient

load_dotenv()

github_base_url = "https://models.github.ai/inference"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_MODEL = os.getenv("GITHUB_MODEL")

if not GITHUB_TOKEN or not GITHUB_MODEL:
    raise ValueError("GITHUB_TOKEN and GITHUB_MODEL must be set in the .env file")


# ---------------------------------------------------------------------------
# Workflow step 1: Triage (Python executor)
# ---------------------------------------------------------------------------


@executor(id="triage_input")
async def triage_input(query: str, ctx: WorkflowContext[str]) -> None:
    """Step 1: Tag the query with a severity level based on keywords."""
    lower = query.lower()
    if any(k in lower for k in ("critical", "down", "outage", "crash", "failed")):
        severity = "CRITICAL"
    elif any(k in lower for k in ("error", "high", "warn", "slow", "alert", "spike")):
        severity = "HIGH"
    else:
        severity = "INFO"
    tagged = f"[{severity}] {query}"
    print(f"  🔍 Step 1 (Triage): {tagged}")
    await ctx.send_message(tagged)


# ---------------------------------------------------------------------------
# Workflow step 3: Capture output (Python executor)
# ---------------------------------------------------------------------------


@executor(id="capture_output")
async def capture_output(
    response: AgentExecutorResponse, ctx: WorkflowContext[None, str]
) -> None:
    """Step 3: Extract the OpsAgent response and yield it as workflow output."""
    print("  ✅ Step 3 (Capture): extracting final output.")
    await ctx.yield_output(response.agent_response.text)


# ---------------------------------------------------------------------------
# Build and run workflow
# ---------------------------------------------------------------------------


async def main() -> None:
    """Build and run the OpsAgent triage workflow."""

    print("🤖 OpsAgent (Workflow) is ready.")
    print(
        "Describe an ops situation — e.g. 'production server is down', 'CPU spike at 95%'."
    )
    print("Type 'exit' to stop.\n")

    async_openai = AsyncOpenAI(
        api_key=GITHUB_TOKEN,
        base_url=github_base_url,
    )

    client = OpenAIChatCompletionClient(
        model=GITHUB_MODEL,
        async_client=async_openai,
    )

    # Step 2: OpsAgent — provides resolution steps for the tagged query.
    # Agent implements AgentProtocol and can be used directly as a workflow executor.
    ops_agent = Agent(
        client=client,
        name="OpsAgent",
        description="OpsAgent is an AI-powered operations and engineering assistant.",
        instructions=(
            "You are OpsAgent, an AI-powered operations and engineering assistant. "
            "You receive tagged ops queries in the format [SEVERITY] description. "
            "Provide concise, actionable resolution steps for the reported issue. "
            "Keep responses short and practical."
        ),
    )

    # Build the workflow: triage_input → ops_agent → capture_output
    # output_from=[capture_output] ensures only the final step's yield_output is collected.
    workflow = (
        WorkflowBuilder(
            start_executor=triage_input,
            output_from=[capture_output],
        )
        .add_edge(triage_input, ops_agent)
        .add_edge(ops_agent, capture_output)
        .build()
    )

    while True:
        try:
            query = input("👤 You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n👋 Goodbye!")
            break

        if not query:
            print("Please enter a message or type 'exit'.")
            continue

        if query.lower() in {"exit", "quit"}:
            print("👋 Goodbye!")
            break

        print()
        result = await workflow.run(query)
        for output in result.get_outputs():
            print(f"💬 OpsAgent: {output}\n")


if __name__ == "__main__":
    asyncio.run(main())
