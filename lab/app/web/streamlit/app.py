"""
Module 9 — OpsAgent Streamlit Web Chat Interface

Streamlit is synchronous, but the agent framework is async. This app uses a
SyncOpsAgent wrapper that keeps a dedicated asyncio event loop running in a
background thread, allowing the agent (with its async HTTP clients and MCP
connections) to stay alive across all turns of a conversation.

  Module 4 — Tool Calling:     Azure health check, deployment checklist, error diagnosis
  Module 5 — MCP Integration:  Microsoft Learn documentation
  Module 6 — Multi-Turn:       Persistent session inside the background thread
  Module 7 — Memory:           UserMemoryProvider remembers the user's name
  Module 8 — Workflow:         Sidebar "Run Triage Workflow" panel

Run from lab/app/web/streamlit/:
    streamlit run app.py
Then open http://localhost:8501 in your browser.
"""

import asyncio
import os
import queue
import sys
import threading
from collections.abc import Generator
from pathlib import Path
from typing import Any, Coroutine, cast

# ---------------------------------------------------------------------------
# Path setup — allows 'from app.shared.X import ...' when Streamlit runs here.
# ---------------------------------------------------------------------------
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

import streamlit as st
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent.parent.parent / ".env")

from app.shared.agent import (
    build_triage_workflow,
    classify_severity,
    create_chat_client,
    create_ops_agent,
)


def _get_required_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        st.error("GITHUB_TOKEN and GITHUB_MODEL must be set in the .env file")
        st.stop()
    return value


GITHUB_TOKEN = _get_required_env("GITHUB_TOKEN")
GITHUB_MODEL = _get_required_env("GITHUB_MODEL")


# ---------------------------------------------------------------------------
# Async-to-sync bridge
#
# Streamlit re-runs the entire script on every user interaction, but each
# re-run must share the same agent and session so conversation history and
# memory are preserved.  SyncOpsAgent solves this by:
#   1. Spinning up a private asyncio event loop in a daemon thread.
#   2. Storing the async agent and session inside that thread.
#   3. Exposing sync .chat() and .run_workflow() methods that submit
#      coroutines to the thread's loop and block for the result.
#
# The instance is stored in st.session_state so each browser tab gets its own
# independent agent (with its own conversation history).
# ---------------------------------------------------------------------------


class SyncOpsAgent:
    """Thread-safe synchronous wrapper around the async OpsAgent."""

    def __init__(self) -> None:
        self._loop = asyncio.new_event_loop()
        # Daemon thread: auto-exits when the Streamlit process exits.
        self._thread = threading.Thread(target=self._loop.run_forever, daemon=True)
        self._thread.start()
        # Initialise the async agent inside the dedicated loop.
        future = asyncio.run_coroutine_threadsafe(self._init(), self._loop)
        self._agent, self._session, self._client = future.result(timeout=30)

    async def _init(self):
        """Create the agent and session (runs in the background thread)."""
        client = create_chat_client(GITHUB_TOKEN, GITHUB_MODEL)
        agent = create_ops_agent(client)
        # Initialise agent resources (MCP tool connections etc.)
        await agent.__aenter__()
        session = agent.create_session()
        return agent, session, client

    def chat(self, message: str) -> str:
        """Send a message to OpsAgent and return the response text (blocking)."""

        async def _run_chat():
            return await self._agent.run(message, session=self._session)

        future = asyncio.run_coroutine_threadsafe(
            cast(Coroutine[Any, Any, Any], _run_chat()),
            self._loop,
        )
        return future.result(timeout=60).text

    def chat_stream(self, message: str) -> Generator[dict, None, None]:
        """Stream response events (text tokens and tool-call markers) via a queue."""
        q: queue.Queue[dict] = queue.Queue()

        async def _run():
            async for chunk in self._agent.run(
                message, stream=True, session=self._session
            ):
                for content in chunk.contents or []:
                    q.put(
                        {
                            "type": content.type,
                            "text": content.text,
                            "tool_name": getattr(content, "tool_name", None),
                        }
                    )
            q.put({"type": "done"})

        asyncio.run_coroutine_threadsafe(
            cast(Coroutine[Any, Any, Any], _run()), self._loop
        )

        while True:
            event = q.get()
            if event["type"] == "done":
                break
            yield event

    def run_workflow(self, query: str) -> tuple[str, str]:
        """Run the triage workflow and return (severity_label, response_text)."""
        severity = classify_severity(query)
        workflow = build_triage_workflow(self._client)

        async def _run_workflow():
            return await workflow.run(query)

        future = asyncio.run_coroutine_threadsafe(
            cast(Coroutine[Any, Any, Any], _run_workflow()),
            self._loop,
        )
        result = future.result(timeout=60)
        outputs = result.get_outputs()
        return severity, (outputs[0] if outputs else "(no output)")

    def get_session_state(self) -> dict:
        """Return a dict of observable session state values."""
        provider_state = self._session.state.get("user_memory", {})
        return {"user_name": provider_state.get("user_name", "(not set)")}


# ---------------------------------------------------------------------------
# Page configuration
# ---------------------------------------------------------------------------

st.set_page_config(page_title="OpsAgent", page_icon="🤖", layout="wide")

# ---------------------------------------------------------------------------
# Per-browser-tab session initialisation
# ---------------------------------------------------------------------------

if "ops_agent" not in st.session_state:
    with st.spinner("Initialising OpsAgent…"):
        st.session_state.ops_agent = SyncOpsAgent()

if "messages" not in st.session_state:
    st.session_state.messages = []

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------

with st.sidebar:
    st.title("🤖 OpsAgent")
    st.caption("Module 9 — Chat User Interface")
    st.divider()

    st.markdown(
        "**Active features:**\n\n"
        "- ✅ Module 4 — Tools\n"
        "- ✅ Module 5 — MCP\n"
        "- ✅ Module 6 — Multi-Turn\n"
        "- ✅ Module 7 — Memory\n"
        "- ✅ Module 8 — Workflow"
    )
    st.divider()

    # Workflow panel (Module 8)
    st.markdown("**🔍 Triage Workflow**")
    workflow_query = st.text_input(
        "Ops query", placeholder="e.g. production server is down"
    )
    run_workflow_btn = st.button("▶ Run Workflow", use_container_width=True)

    st.divider()

    # Session state viewer (Module 7)
    state = st.session_state.ops_agent.get_session_state()
    st.markdown("**📦 Session State**")
    st.code(f"user_name: {state['user_name']}", language="text")

    st.divider()
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# ---------------------------------------------------------------------------
# Workflow run (triggered from sidebar button)
# ---------------------------------------------------------------------------

if run_workflow_btn and workflow_query:
    with st.spinner("Running triage workflow…"):
        severity, wf_response = st.session_state.ops_agent.run_workflow(workflow_query)
    wf_content = (
        f"**🔍 Triage Workflow** — Severity: `{severity}`\n\n"
        f"**Query:** {workflow_query}\n\n{wf_response}"
    )
    st.session_state.messages.append({"role": "assistant", "content": wf_content})
    st.rerun()

# ---------------------------------------------------------------------------
# Main chat area
# ---------------------------------------------------------------------------

st.title("OpsAgent")
st.caption(
    "Ask about Azure ops, deployments, or errors. "
    "I remember your name — try: 'My name is Alex.'"
)

# Display conversation history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat input
if prompt := st.chat_input("Ask OpsAgent…"):
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        status = st.status("Thinking…", expanded=False)
        text_box = st.empty()
        full_text = ""

        for event in st.session_state.ops_agent.chat_stream(prompt):
            if event["type"] == "function_call":
                tool = event.get("tool_name") or "tool"
                status.update(label=f"⚙ Calling {tool}…", state="running")
            elif event["type"] == "function_result":
                status.update(label="⚙ Processing result…", state="running")
            elif event["type"] == "text" and event.get("text"):
                full_text += event["text"]
                text_box.markdown(full_text)

        status.update(label="Done", state="complete", expanded=False)

    st.session_state.messages.append({"role": "assistant", "content": full_text})
