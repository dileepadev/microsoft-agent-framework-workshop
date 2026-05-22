"""
Module 9 -- OpsAgent CLI Chat Interface

Full-featured interactive command-line interface combining every workshop module:

  Module 4 -- Tool Calling:     Azure health check, deployment checklist, error diagnosis
  Module 5 -- MCP Integration:  Microsoft Learn documentation tool
  Module 6 -- Multi-Turn:       Persistent conversation history via session
  Module 7 -- Memory:           UserMemoryProvider remembers your name across turns
  Module 8 -- Workflow:         Run !workflow <query> to trigger the triage pipeline

Responses are streamed token-by-token. Animated spinners show what OpsAgent is
doing at each stage: thinking -> calling tool -> generating response -> streaming.

Run from the lab/ folder:
    python app/cli/main.py
    uv run app/cli/main.py

Special commands while chatting:
  !help              Show this message
  !state             Show current session state (stored user info)
  !workflow <query>  Run the ops triage workflow pipeline on <query>
  exit / quit        Exit
"""

import asyncio
import itertools
import os
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Path setup -- allows 'from app.shared.X import ...' when running from lab/.
# ---------------------------------------------------------------------------
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent.parent / ".env")

from app.shared.agent import (
    build_triage_workflow,
    classify_severity,
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

# ---------------------------------------------------------------------------
# UI strings
# ---------------------------------------------------------------------------

BANNER = """\
╔══════════════════════════════════════════════════════════════════╗
║        OpsAgent CLI  --  Module 9: Chat User Interface           ║
╚══════════════════════════════════════════════════════════════════╝
  Active features:
   ✅  Module 4  Tool Calling    Azure health, deployment checklist, error diagnosis
   ✅  Module 5  MCP             Microsoft Learn documentation
   ✅  Module 6  Multi-Turn      Persistent conversation history
   ✅  Module 7  Memory          Remembers your name across turns
   ✅  Module 8  Workflow        Run with  !workflow <query>

  Type  !help  for commands.   Type  exit  to quit.
"""

HELP_TEXT = """\
Commands:
  !help              Show this message
  !state             Show current session state (stored user info)
  !workflow <query>  Run the ops triage workflow pipeline on <query>
  exit / quit        Exit the CLI
"""

# ---------------------------------------------------------------------------
# Async spinner
# ---------------------------------------------------------------------------

_SPINNER_FRAMES = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
_SPINNER_WIDTH = 60  # characters reserved for the spinner line


class Spinner:
    """
    Async spinner that animates in-place using carriage returns.

    Usage (within an async context)::

        spinner = Spinner("Thinking...")
        spinner.start()
        ...
        spinner.update("Calling tool...")   # change label without restarting
        ...
        await spinner.stop()               # clears the line and finishes
    """

    def __init__(self, message: str = "") -> None:
        self.message = message
        self._task: asyncio.Task | None = None
        self._stop_event: asyncio.Event = asyncio.Event()

    async def _run(self) -> None:
        for frame in itertools.cycle(_SPINNER_FRAMES):
            if self._stop_event.is_set():
                break
            line = f"  {frame}  {self.message}"
            print(f"\r{line:{_SPINNER_WIDTH}}", end="", flush=True)
            await asyncio.sleep(0.08)
        # Clear the spinner line on exit.
        print(f"\r{' ' * _SPINNER_WIDTH}\r", end="", flush=True)

    def start(self) -> None:
        """Schedule the spinner animation as a background task."""
        self._stop_event.clear()
        self._task = asyncio.ensure_future(self._run())

    def update(self, message: str) -> None:
        """Change the label without stopping the animation."""
        self.message = message

    async def stop(self) -> None:
        """Signal the animation to stop and wait for the task to finish."""
        if self._task is None or self._stop_event.is_set():
            return
        self._stop_event.set()
        await self._task
        self._task = None


# ---------------------------------------------------------------------------
# Streaming chat response
# ---------------------------------------------------------------------------


async def stream_response(agent, message: str, session) -> None:
    """
    Stream OpsAgent's response with context-aware spinners.

    Phase transitions driven by content types in the stream:
      function_call   --> "Calling tool..."
      function_result --> "Generating response..."
      text            --> stop spinner, print tokens live
    """
    spinner = Spinner("Thinking...")
    spinner.start()

    phase = "thinking"  # thinking | tool | tool_done | generating | streaming

    async for chunk in agent.run(message, stream=True, session=session):
        for content in chunk.contents or []:
            ctype = content.type

            if ctype == "function_call":
                if phase in ("thinking", "tool_done"):
                    spinner.update("⚙  Calling tool...")
                    phase = "tool"

            elif ctype == "function_result":
                if phase == "tool":
                    spinner.update("Generating response...")
                    phase = "tool_done"

            elif ctype == "text" and content.text:
                if phase != "streaming":
                    # First text token -- clear spinner, print the prefix.
                    await spinner.stop()
                    print("\n💬 OpsAgent: ", end="", flush=True)
                    phase = "streaming"
                print(content.text, end="", flush=True)

    if phase == "streaming":
        print("\n")  # newline after the last streamed token
    else:
        # Edge case: no text produced (pure tool call with no follow-up text).
        await spinner.stop()
        print()


# ---------------------------------------------------------------------------
# Workflow with spinner
# ---------------------------------------------------------------------------


async def run_triage_workflow(query: str, client) -> None:
    """Run the Module 8 triage workflow with a live spinner."""
    severity = classify_severity(query)
    print(f"\n  🔍 Triage:  [{severity}] {query}")

    spinner = Spinner("Running workflow pipeline...")
    spinner.start()
    try:
        workflow = build_triage_workflow(client)
        result = await workflow.run(query)
    finally:
        await spinner.stop()

    outputs = result.get_outputs()
    print(f"\n  💬 OpsAgent (Workflow):\n{outputs[0] if outputs else '(no output)'}\n")


# ---------------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------------


async def main() -> None:
    print(BANNER)

    client = create_chat_client(GITHUB_TOKEN, GITHUB_MODEL)

    # async with properly initialises and later cleans up any MCP tool connections.
    async with create_ops_agent(client) as agent:
        session = agent.create_session()

        while True:
            try:
                raw = input("👤 You: ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\n👋 Goodbye!")
                break

            if not raw:
                continue

            # --- Built-in commands ---
            if raw.lower() in {"exit", "quit"}:
                provider_state = session.state.get("user_memory", {})
                stored_name = provider_state.get("user_name")
                if stored_name:
                    print(f"\n📦 Session State: stored user name --> {stored_name}")
                print("👋 Goodbye!")
                break

            if raw == "!help":
                print(HELP_TEXT)
                continue

            if raw == "!state":
                provider_state = session.state.get("user_memory", {})
                stored_name = provider_state.get("user_name", "(not set yet)")
                print(f"\n📦 Session State --> user_name: {stored_name}\n")
                continue

            if raw.startswith("!workflow"):
                query = raw[len("!workflow") :].strip()
                if not query:
                    print("Usage: !workflow <your ops query>\n")
                else:
                    await run_triage_workflow(query, client)
                continue

            if raw.startswith("!"):
                print(f"Unknown command '{raw}'. Try !help.\n")
                continue

            # --- Streaming multi-turn chat (Modules 6 + 7) ---
            print()
            await stream_response(agent, raw, session)


if __name__ == "__main__":
    asyncio.run(main())
