"""
Module 9 — OpsAgent Chainlit Web Chat Interface

Chainlit provides a ready-made chat UI. This app wires OpsAgent into it
with every workshop module active in the same session.

  Module 4 — Tool Calling:     Azure health check, deployment checklist, error diagnosis
  Module 5 — MCP Integration:  Microsoft Learn documentation
  Module 6 — Multi-Turn:       session persists for the lifetime of the chat window
  Module 7 — Memory:           UserMemoryProvider remembers the user's name
  Module 8 — Workflow:         type  /workflow <query>  in the chat input

Run from lab/app/web/chainlit/:
    chainlit run app.py
Then open http://localhost:8000 in your browser.
"""

import json
import os
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Path setup — allows 'from app.shared.X import ...' when Chainlit runs here.
# ---------------------------------------------------------------------------
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

import chainlit as cl
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent.parent.parent / ".env")

from app.shared.agent import (
    build_triage_workflow,
    create_chat_client,
    create_ops_agent,
)


def _get_required_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise ValueError("GITHUB_TOKEN and GITHUB_MODEL must be set in the .env file")
    return value


GITHUB_TOKEN = _get_required_env("GITHUB_TOKEN")
GITHUB_MODEL = _get_required_env("GITHUB_MODEL")


def _format_step_name(call_name: str) -> str:
    """Return a readable label that distinguishes MCP calls from regular tools."""
    if call_name.startswith("microsoft_"):
        return f"MCP: {call_name}"
    return f"Tool: {call_name}"


def _format_step_input(arguments: str) -> str:
    """Pretty-print JSON arguments when possible."""
    if not arguments:
        return ""
    try:
        return json.dumps(json.loads(arguments), indent=2)
    except json.JSONDecodeError:
        return arguments


def _format_step_output(result: object) -> str:
    """Summarize tool results for display in the Chainlit step UI."""
    if result is None:
        return ""

    if isinstance(result, str):
        raw_text = result
    else:
        raw_text = json.dumps(result, indent=2, default=str)

    try:
        payload = json.loads(raw_text)
    except json.JSONDecodeError:
        payload = None

    if isinstance(payload, dict) and isinstance(payload.get("results"), list):
        results = payload["results"]
        preview = []
        for entry in results[:3]:
            if isinstance(entry, dict):
                title = entry.get("title") or entry.get("contentUrl") or "(untitled)"
                preview.append(f"- {title}")
        summary = f"Returned {len(results)} result(s)"
        if preview:
            return summary + "\n" + "\n".join(preview)
        return summary

    if len(raw_text) > 1200:
        return raw_text[:1200] + "\n..."
    return raw_text


WELCOME_MESSAGE = """\
# OpsAgent

OpsAgent is your AI-powered operations and engineering assistant. I can help you triage and resolve issues with your Azure services, using a combination of built-in tools, Microsoft Learn documentation, and memory of our conversation.

## What I Can Do

- **Tools**: Check Azure service health, create deployment checklists, and diagnose common errors.
- **MCP**: Query Microsoft Learn for official Azure guidance and troubleshooting steps.
- **Workflow**: Run `/workflow <query>` to classify severity and execute the triage pipeline.
- **Memory**: Remember your name and keep conversation context for this session.

## Try These Examples

- Tool call: `Check Azure App Service health in East US`
- MCP lookup: `Use Microsoft Learn to explain how to restart an Azure App Service`
- Workflow: `/workflow production web app is down and requests are timing out`
- Memory: `My name is Alex` then `What is my name?`

I will stream the answer live and show tool or MCP steps as they happen.
"""


# ---------------------------------------------------------------------------
# Lifecycle callbacks
# ---------------------------------------------------------------------------


@cl.on_chat_start
async def on_chat_start() -> None:
    """Initialise OpsAgent and its session for this chat window."""
    client = create_chat_client(GITHUB_TOKEN, GITHUB_MODEL)
    agent = create_ops_agent(client)

    # Initialise agent resources (MCP tool connections etc.)
    await agent.__aenter__()

    session = agent.create_session()

    cl.user_session.set("agent", agent)
    cl.user_session.set("client", client)
    cl.user_session.set("session", session)

    await cl.Message(content=WELCOME_MESSAGE).send()


@cl.on_message
async def on_message(message: cl.Message) -> None:
    """Handle every user message."""
    content = message.content.strip()

    agent = cl.user_session.get("agent")
    client = cl.user_session.get("client")
    session = cl.user_session.get("session")
    assert agent is not None and client is not None and session is not None

    # -----------------------------------------------------------------------
    # /workflow command — runs the Module 8 triage pipeline
    # -----------------------------------------------------------------------
    if content.lower().startswith("/workflow"):
        query = content[len("/workflow") :].strip()
        if not query:
            await cl.Message(content="Usage: `/workflow <your ops query>`").send()
            return

        thinking = cl.Message(content="🔍 Running triage workflow…")
        await thinking.send()

        workflow = build_triage_workflow(client)
        result = await workflow.run(query)
        outputs = result.get_outputs()
        response = outputs[0] if outputs else "(no output)"

        thinking.content = f"**🔍 Workflow Result:**\n\n{response}"
        await thinking.update()
        return

    # -----------------------------------------------------------------------
    # Normal turn — multi-turn history (Module 6) + memory (Module 7)
    # -----------------------------------------------------------------------
    response_msg = cl.Message(content="")
    current_step: cl.Step | None = None
    current_step_name = ""
    current_step_arguments = ""

    async for chunk in agent.run(content, stream=True, session=session):
        for item in chunk.contents or []:
            if item.type == "function_call":
                call_name = (getattr(item, "name", None) or "").strip()
                call_arguments = getattr(item, "arguments", None) or ""

                # The stream emits one named function_call followed by unnamed
                # argument fragments. Aggregate them into a single visible step.
                if call_name:
                    if current_step is not None:
                        current_step.input = _format_step_input(current_step_arguments)
                        await current_step.update()
                        await current_step.__aexit__(None, None, None)

                    current_step_name = call_name
                    current_step_arguments = call_arguments
                    current_step = cl.Step(
                        name=_format_step_name(call_name),
                        type="tool",
                        default_open=True,
                    )
                    await current_step.__aenter__()
                elif current_step is not None and call_arguments:
                    current_step_arguments += call_arguments

            elif item.type == "function_result":
                if current_step is not None:
                    current_step.input = _format_step_input(current_step_arguments)
                    current_step.output = _format_step_output(
                        getattr(item, "result", None)
                    )
                    await current_step.update()
                    await current_step.__aexit__(None, None, None)
                    current_step = None
                    current_step_name = ""
                    current_step_arguments = ""

            elif item.type == "text" and item.text:
                await response_msg.stream_token(item.text)

    if current_step is not None:
        current_step.input = _format_step_input(current_step_arguments)
        await current_step.update()
        await current_step.__aexit__(None, None, None)

    await response_msg.send()


@cl.on_chat_end
async def on_chat_end() -> None:
    """Release agent resources when the chat session ends."""
    agent = cl.user_session.get("agent")
    if agent is not None:
        await agent.__aexit__(None, None, None)
