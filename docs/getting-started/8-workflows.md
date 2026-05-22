# 8. Workflows

In this module, you build a multi-step workflow where each executor processes data and passes it to the next — chaining a Python triage step, an OpsAgent LLM step, and a Python capture step into a single automated pipeline.

## Module Goals

By the end of this module, you will be able to:

- Define workflow steps using the `@executor` decorator
- Use an `Agent` (with GitHub Models) as a step inside a workflow
- Connect steps with directed edges using `WorkflowBuilder`
- Run the workflow and read its output with `workflow.run()`

## In This Module

- Why Workflows Matter
- Step 1 through Step 5
- Expected Outcomes

## Why Workflows Matter

Single-agent calls work well for one-off questions. But in real ops work, you often need a small pipeline where each step has one clear job. In this module, we keep it simple with one pipeline centered on OpsAgent.

Think of this workflow as 3 boxes:

1. Python triage step tags severity
2. OpsAgent generates actionable steps
3. Python capture step returns final output

Microsoft Agent Framework **Workflows** let you express this as a directed graph:

- **Executors** — the individual processing steps (Python functions or Agents)
- **Edges** — the connections between steps that route messages forward
- **WorkflowBuilder** — the fluent API that wires it all together

```text
triage_input  ──▶  ops_agent  ──▶  capture_output
 (Python)           (LLM)            (Python)
```

There are two workflow APIs:

| API | When to use |
| --- | --- |
| `@executor` + `WorkflowBuilder` | Fixed graphs, type-validated routing, fan-out/fan-in |
| `@workflow` + `@step` (functional) | Easiest starting point: sequential pipelines expressed as plain `async` functions |

This module uses the `@executor` + `WorkflowBuilder` approach because it matches this 3-box flow and keeps message movement explicit for beginners.

> [!NOTE]
> Workflows include many advanced concepts (parallel branches, conditional routing, events, supersteps, checkpoints, and more). Covering most of them would make this workshop too broad. That is not the goal of this workshop, so this module focuses only on the introduction you need to get started with OpsAgent workflows.

## Step 1 - Create the Test Script

Inside the [lab/](../../lab/) folder, create the script for this module.

```bash
touch test_workflows.py
```

## Step 2 - Ensure GitHub Environment Variables

Make sure your `.env` includes:

```env
GITHUB_TOKEN=github_pat_...
GITHUB_MODEL=gpt-4o-mini
```

## Step 3 - Define the Workflow Steps (Executors)

Use the `@executor` decorator to create reusable, typed workflow steps.

**Step 1 — `triage_input`**: a Python executor that tags the query with a severity level:

```python
from agent_framework import executor, WorkflowContext

@executor(id="triage_input")
async def triage_input(query: str, ctx: WorkflowContext[str]) -> None:
    lower = query.lower()
    if any(k in lower for k in ("critical", "down", "outage", "crash", "failed")):
        severity = "CRITICAL"
    elif any(k in lower for k in ("error", "high", "warn", "slow", "alert", "spike")):
        severity = "HIGH"
    else:
        severity = "INFO"
    tagged = f"[{severity}] {query}"
    await ctx.send_message(tagged)
```

- `WorkflowContext[str]` — this executor sends `str` messages to the next step
- `ctx.send_message(tagged)` — passes the tagged string to the next executor

**Step 3 — `capture_output`**: a Python executor that extracts text from the OpsAgent response:

```python
from agent_framework import AgentExecutorResponse

@executor(id="capture_output")
async def capture_output(
    response: AgentExecutorResponse, ctx: WorkflowContext[None, str]
) -> None:
    await ctx.yield_output(response.agent_response.text)
```

- `AgentExecutorResponse` — the type produced when an `Agent` is used as a workflow step
- `ctx.yield_output(...)` — marks the value as the final workflow output

## Step 4 - Build the Workflow with WorkflowBuilder

Create the OpsAgent (GitHub Models) and connect all three steps with `WorkflowBuilder`.

```python
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
# output_from=[capture_output] collects only the final step's yield_output.
workflow = (
    WorkflowBuilder(
        start_executor=triage_input,
        output_from=[capture_output],
    )
    .add_edge(triage_input, ops_agent)
    .add_edge(ops_agent, capture_output)
    .build()
)
```

Run the workflow and read the result:

```python
result = await workflow.run(query)
for output in result.get_outputs():
    print(f"💬 OpsAgent: {output}")
```

## Step 5 - Complete Code (Single File)

```python
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
```

## Run the Script

```bash
python test_workflows.py
# or
uv run test_workflows.py
```

## Example Output

```text
🤖 OpsAgent (Workflow) is ready.
Describe an ops situation — e.g. 'production server is down', 'CPU spike at 95%'.
Type 'exit' to stop.

👤 You: production server is down!

  🔍 Step 1 (Triage): [CRITICAL] production server is down!
  ✅ Step 3 (Capture): extracting final output.
💬 OpsAgent: 1. Verify the server is actually down (ping the server, check logs).
2. Access the server console via management tools or recovery mode if needed.
3. Restart the server if possible.
4. Check for hardware issues (overheating, power supply).
5. Review recent changes (updates, deployments) that may have caused the outage.
6. Implement failover or switch to a backup server if necessary.
7. Communicate with stakeholders on status and expected resolution timeline.

👤 You: CPU spike at 95%

  🔍 Step 1 (Triage): [HIGH] CPU spike at 95%
  ✅ Step 3 (Capture): extracting final output.
💬 OpsAgent: 1. Identify the process causing the spike using top or htop.
2. Check for runaway processes or infinite loops and restart if needed.
3. Review recent deployments or scheduled jobs that may explain the spike.
4. Scale horizontally if load is legitimate traffic.
5. Set CPU alerts to catch future spikes earlier.

👤 You: exit
👋 Goodbye!
```

## Expected Outcomes

- Step 1 tags the input as `[CRITICAL]`, `[HIGH]`, or `[INFO]` based on keywords
- Step 2 (OpsAgent) receives the tagged query and generates resolution steps using GitHub Models
- Step 3 extracts the agent's text response and yields it as the workflow output
- `result.get_outputs()` returns exactly one item — the captured final output

## Key Concepts

| Concept | Description |
| --- | --- |
| `@executor` decorator | Turns an `async` function into a typed workflow step |
| `WorkflowContext[Out]` | Generic that specifies the message type sent to the next step |
| `ctx.send_message(value)` | Passes data forward to the next executor in the graph |
| `ctx.yield_output(value)` | Marks the value as a final workflow output |
| `AgentExecutorResponse` | The message type produced when an `Agent` runs as a workflow step |
| `WorkflowBuilder` | Fluent API for connecting executors into a directed graph |
| `add_edge(source, target)` | Adds a directed edge from one executor to the next |
| `output_from=[executor]` | Specifies which executors' `yield_output` values to collect |
| `workflow.run(input)` | Runs the workflow and returns a `WorkflowRunResult` |
| `result.get_outputs()` | Returns the list of final outputs from the workflow |

## Next

Continue to [9. Chat User Interface](9-chat-user-interface)
