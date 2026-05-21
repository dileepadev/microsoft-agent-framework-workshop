# 7. Memory & Persistence

In this module, you give OpsAgent a memory — the ability to remember facts about the user across turns and inject them as personalized instructions on each call.

You will implement a custom `ContextProvider` that stores a user's name in session state and injects it into the agent's instructions before every run.

## Module Goals

By the end of this module, you will be able to:

- Build a custom `ContextProvider` that reads and writes session state
- Inject personalized instructions into the agent on each turn
- Extract facts from user messages and persist them in session state
- Use `InMemoryHistoryProvider` alongside your custom provider

## In This Module

- Why Memory & Persistence Matters
- Step 1 through Step 5
- Expected Outcomes

## Multi-Turn vs Memory & Persistence

These two concepts are related but solve different problems:

| | Multi-Turn Conversations | Memory & Persistence |
| --- | --- | --- |
| **What it solves** | Agent forgets what was said in the same conversation | Agent forgets facts about the user across calls |
| **Mechanism** | `AgentSession` maintains a message buffer across `agent.run()` calls | `ContextProvider` stores facts in session state and injects them as instructions |
| **Scope** | Conversation history (the back-and-forth messages) | User facts and preferences (name, preferences, context) |
| **Example** | "What did I just ask you?" → agent recalls the earlier message | "What is my name?" → agent recalls the name you told it earlier |
| **Module** | [Module 6](6-multi-turn-conversations.md) | This module |

In practice, you use **both together**: a session keeps conversation history, and a context provider injects facts on top of it.

## Why Memory & Persistence Matters

By default an agent is stateless — it has no memory of who the user is or what was said before. For personalized or long-running assistants, you want the agent to:

- Remember facts (e.g. the user's name, preferences)
- Inject those facts as instructions before each call
- Accumulate state across turns without re-sending every message

Microsoft Agent Framework solves this with **context providers**. A `ContextProvider` hooks into every `agent.run()` call via two methods:

| Method | When it runs | Purpose |
| --- | --- | --- |
| `before_run` | Before the model call | Inject instructions, messages, or tools |
| `after_run` | After the model call | Extract and store facts from the conversation |

Session state (the `state` dict passed to each hook) is **scoped per provider** and persisted in the `AgentSession` — so state you write in `after_run` is available to `before_run` on the next turn.

## Step 1 - Create the Test Script

Inside the [lab/](../../lab/) folder, create the script for this module.

```bash
touch test_memory_persistence.py
```

## Step 2 - Ensure GitHub Environment Variables

Make sure your `.env` includes:

```env
GITHUB_TOKEN=github_pat_...
GITHUB_MODEL=gpt-4o-mini
```

## Step 3 - Define the UserMemoryProvider

Subclass `ContextProvider` to create a provider that remembers the user's name.

**`before_run`** — inject a personalization instruction before each call:

```python
async def before_run(self, *, agent, session, context, state):
    user_name = state.get("user_name")
    if user_name:
        context.extend_instructions(
            self.source_id,
            f"The user's name is {user_name}. Always address them by name.",
        )
    else:
        context.extend_instructions(
            self.source_id,
            "You don't know the user's name yet. Ask for it politely.",
        )
```

**`after_run`** — extract the name from the user's messages and store it:

```python
async def after_run(self, *, agent, session, context, state):
    for msg in context.get_messages():
        text = msg.text if hasattr(msg, "text") else ""
        if isinstance(text, str) and "my name is" in text.lower():
            name = text.lower().split("my name is")[-1].strip().split()[0].strip(".,!?;:").capitalize()
            state["user_name"] = name
```

> **Note:** The `state` dict passed to each hook is **provider-scoped** (as of agent-framework 1.0.0rc1). Access your values with `state["key"]` directly — not `state[self.source_id]["key"]`.

## Step 4 - Register Providers and Create Agent

Pass both the custom memory provider and `InMemoryHistoryProvider` via `context_providers`.

```python
agent = Agent(
    client=client,
    name="OpsAgent",
    description="OpsAgent is an AI-powered operations and engineering assistant.",
    instructions=(
        "You are OpsAgent, an AI-powered operations and engineering assistant. "
        "Help developers and cloud engineers troubleshoot issues, retrieve documentation, "
        "analyze systems, and automate operational workflows. "
        "Keep responses concise, actionable, and practical."
    ),
    context_providers=[
        UserMemoryProvider(),
        # Persists conversation history across turns.
        # Only one history provider should have load_messages=True.
        InMemoryHistoryProvider(load_messages=True),
    ],
)

session = agent.create_session()
```

## Step 5 - Complete Code (Single File)

```python
"""
Module 7 - Test Memory & Persistence with OpsAgent

Run:
    python test_memory_persistence.py
    or
    uv run test_memory_persistence.py
"""

import asyncio
import os
from typing import Any

from dotenv import load_dotenv
from openai import AsyncOpenAI

from agent_framework import (
    Agent,
    AgentSession,
    ContextProvider,
    InMemoryHistoryProvider,
    SessionContext,
)
from agent_framework.openai import OpenAIChatCompletionClient

load_dotenv()

github_base_url = "https://models.github.ai/inference"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_MODEL = os.getenv("GITHUB_MODEL")

if not GITHUB_TOKEN or not GITHUB_MODEL:
    raise ValueError("GITHUB_TOKEN and GITHUB_MODEL must be set in the .env file")


class UserMemoryProvider(ContextProvider):
    """Remembers user info in session state and injects personalization instructions."""

    DEFAULT_SOURCE_ID = "user_memory"

    def __init__(self):
        super().__init__(self.DEFAULT_SOURCE_ID)

    async def before_run(
        self,
        *,
        agent: Any,
        session: AgentSession,
        context: SessionContext,
        state: dict[str, Any],
    ) -> None:
        """Inject personalization instructions based on stored user info."""
        user_name = state.get("user_name")
        if user_name:
            context.extend_instructions(
                self.source_id,
                f"The user's name is {user_name}. Always address them by name.",
            )
        else:
            context.extend_instructions(
                self.source_id,
                "You don't know the user's name yet. Ask for it politely.",
            )

    async def after_run(
        self,
        *,
        agent: Any,
        session: AgentSession,
        context: SessionContext,
        state: dict[str, Any],
    ) -> None:
        """Extract and store user info in session state after each call."""
        for msg in context.get_messages():
            text = msg.text if hasattr(msg, "text") else ""
            if isinstance(text, str) and "my name is" in text.lower():
                name = text.lower().split("my name is")[-1].strip().split()[0].strip(".,!?;:").capitalize()
                state["user_name"] = name


async def main():
    """Create and run OpsAgent with memory and persistence via context providers."""

    print("🤖 OpsAgent (Memory) is ready.")
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
            "Keep responses concise, actionable, and practical."
        ),
        context_providers=[
            UserMemoryProvider(),
            InMemoryHistoryProvider(load_messages=True),
        ],
    )

    session = agent.create_session()

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
            provider_state = session.state.get("user_memory", {})
            stored_name = provider_state.get("user_name")
            if stored_name:
                print(f"\n📦 Session State: Stored user name → {stored_name}")
            print("👋 Goodbye!")
            break

        result = await agent.run(query, session=session)
        print(f"💬 OpsAgent: {result.text}\n")


if __name__ == "__main__":
    asyncio.run(main())
```

## Run the Script

```bash
python test_memory_persistence.py
# or
uv run test_memory_persistence.py
```

## Example Output

```text
🤖 OpsAgent (Memory) is ready.
Type 'exit' to stop.

👤 You: Hello!
💬 OpsAgent: Hello! How can I assist you today? May I know your name?

👤 You: My name is Alice.
💬 OpsAgent: Nice to meet you, Alice! How can I assist you today?

👤 You: What is my name?
💬 OpsAgent: Your name is Alice. How can I help you today?

👤 You: exit

📦 Session State: Stored user name → Alice
👋 Goodbye!
```

## Expected Outcomes

- On the first turn, the agent asks for the user's name (instruction injected by `UserMemoryProvider`)
- After the user says "My name is Alice", the name is stored in session state via `after_run`
- On subsequent turns, the agent always addresses the user by name (instruction updated in `before_run`)
- On exit, the stored session state is printed — confirming persistence across turns

## Key Concepts

| Concept | Description |
| --- | --- |
| `ContextProvider` | Base class for custom before/after run hooks |
| `before_run` | Inject dynamic instructions, messages, or tools each turn |
| `after_run` | Extract facts and write them into provider-scoped session state |
| `context.extend_instructions` | Append personalization to the agent's system prompt |
| `InMemoryHistoryProvider` | Built-in provider that persists conversation history locally |
| Provider-scoped state | `state["key"]` in hooks — scoped to this provider automatically |

## Next

Continue to [Module 8 - Chat User Interface](8-chat-user-interface.md)
