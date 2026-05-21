# 6. Multi-Turn Conversations

In this module, you enable OpsAgent to remember user context across multiple turns by reusing an `AgentSession`.

You will now run the same script in two modes to compare behavior:

- `session`: remembers previous turns
- `stateless`: treats each turn independently

## Module Goals

By the end of this module, you will be able to:

- Keep context between user turns using a session
- Compare session vs stateless behavior in one script
- Ask follow-up questions that depend on earlier messages
- Build a simple conversation loop with exit controls

## In This Module

- Why Multi-Turn Matters
- Step 1 through Step 5
- Expected Outcomes

## Why Multi-Turn Matters

By default, one-shot calls are stateless. For conversation-style apps, you need session state so the agent can remember prior turns.

Microsoft Learn shows this pattern with `AgentSession`:

- Create a session once: `session = agent.create_session()`
- Pass that session on each call: `await agent.run(query, session=session)`

This module uses the same pattern, but with GitHub Models (not Foundry client setup), consistent with earlier modules in this workshop.

## Step 1 - Create the Test Script

Inside [lab/test_multi_turn_conversations.py](../../lab/test_multi_turn_conversations.py), add the script for this module.

```bash
touch test_multi_turn_conversations.py
```

## Step 2 - Ensure GitHub Environment Variables

Make sure your `.env` includes:

```env
GITHUB_TOKEN=github_pat_...
GITHUB_MODEL=gpt-4o-mini
```

## Step 3 - Build Agent and Create Session

Create the GitHub Models client and an `Agent`. Then create a session only when running in `session` mode.

```python
agent = Agent(
    client=client,
    name="OpsAgent",
    description="OpsAgent is an AI-powered operations and engineering assistant.",
    instructions=(
        "You are OpsAgent, an AI-powered operations and engineering assistant. "
        "Keep your answers brief and helpful."
    ),
)

# Keep a single session alive so earlier turns remain available.
session = agent.create_session() if mode == "session" else None
```

## Step 4 - Run a Multi-Turn Loop

Read user input repeatedly. The same loop works for both modes.

```python
while True:
    query = input("👤 You: ").strip()
    if query.lower() in {"exit", "quit"}:
        break

    # In session mode, this preserves conversation memory.
    # In stateless mode, session is None, so each turn is independent.
    result = await agent.run(query, session=session)
    print(f"💬 OpsAgent: {result.text}\n")
```

## Step 5 - Complete Code (Single File)

```python
"""
Module 6 - Test Multi-Turn Conversations with OpsAgent

Run:
    python test_multi_turn_conversations.py
    or
    uv run test_multi_turn_conversations.py
"""

import asyncio
import argparse
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


def parse_args() -> argparse.Namespace:
    """Parse optional mode argument for session behavior."""

    parser = argparse.ArgumentParser(
        description="Run OpsAgent in session or stateless mode.",
    )
    parser.add_argument(
        "--mode",
        choices=["session", "stateless"],
        help="Execution mode. If omitted, an interactive choice is shown.",
    )
    return parser.parse_args()


def choose_mode(cli_mode: str | None) -> str:
    """Choose mode from CLI or interactive prompt."""

    if cli_mode:
        return cli_mode

    print("Choose mode:")
    print("  1) session   - remembers previous messages")
    print("  2) stateless - each turn is independent")

    while True:
        choice = input("Select mode (1/2): ").strip()
        if choice == "1":
            return "session"
        if choice == "2":
            return "stateless"
        print("Please enter 1 or 2.")


async def main():
    """Create and run OpsAgent in session or stateless mode."""

    args = parse_args()
    mode = choose_mode(args.mode)

    print(f"\n🤖 OpsAgent ({mode}) is ready.")
    print("Type 'exit' to stop.\n")

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
        instructions=(
            "You are OpsAgent, an AI-powered operations and engineering assistant. "
            "Help developers and cloud engineers troubleshoot issues, retrieve documentation, "
            "analyze systems, and automate operational workflows. "
            "Keep responses concise, actionable, and practical. "
            "Use conversation context from earlier turns when relevant."
        ),
    )

    # In session mode, keep one session alive so prior turns are remembered.
    session = agent.create_session() if mode == "session" else None

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

        result = await agent.run(query, session=session)
        print(f"💬 OpsAgent: {result.text}\n")


if __name__ == "__main__":
    asyncio.run(main())
```

### Run the Script

```bash
python test_multi_turn_conversations.py --mode session
# or
python test_multi_turn_conversations.py --mode stateless
# or choose mode interactively
python test_multi_turn_conversations.py
```

### Example Comparison

```text
[Session Mode]
👤 You: My name is Alice and I love hiking.
💬 OpsAgent: Nice to meet you, Alice. Hiking sounds awesome.

👤 You: What do you remember about me?
💬 OpsAgent: You said your name is Alice and that you love hiking.

[Stateless Mode]
👤 You: My name is Alice and I love hiking.
💬 OpsAgent: Nice to meet you, Alice. Hiking sounds awesome.

👤 You: What do you remember about me?
💬 OpsAgent: I do not have memory of earlier turns in this mode.
```

## Expected Outcomes

- OpsAgent runs with GitHub Models configuration
- The same script supports `session` and `stateless` modes
- In session mode, follow-up questions can reference earlier context
- In stateless mode, each question is treated independently
- Users can end the loop cleanly with `exit` or `quit`

## Next

Continue to [7. Memory and Persistence](./7-memory-and-persistence.md).
