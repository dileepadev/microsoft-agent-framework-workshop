"""
Shared context providers — Module 7 (Memory & Persistence).

UserMemoryProvider detects the user's name from conversation messages and
injects it back as a personalization instruction on subsequent turns.
"""

from typing import Any

from agent_framework import AgentSession, ContextProvider, SessionContext


class UserMemoryProvider(ContextProvider):
    """
    Remembers the user's name in session state and injects it into OpsAgent's
    instructions so every response is addressed to them by name.

    How it works:
      before_run — reads state["user_name"] and adds a personalization instruction.
      after_run  — scans new messages for "my name is …" and saves the name to state.
    """

    DEFAULT_SOURCE_ID = "user_memory"

    def __init__(self) -> None:
        super().__init__(self.DEFAULT_SOURCE_ID)

    async def before_run(
        self,
        *,
        agent: Any,
        session: AgentSession,
        context: SessionContext,
        state: dict[str, Any],
    ) -> None:
        """Inject a personalization instruction before each agent turn."""
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
        """Scan new messages for 'my name is …' and persist the name to state."""
        for msg in context.get_messages():
            text = msg.text if hasattr(msg, "text") else ""
            if isinstance(text, str) and "my name is" in text.lower():
                name = (
                    text.lower()
                    .split("my name is")[-1]
                    .strip()
                    .split()[0]
                    .strip(".,!?;:")
                    .capitalize()
                )
                state["user_name"] = name
