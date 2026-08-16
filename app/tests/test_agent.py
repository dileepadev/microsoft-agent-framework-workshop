"""
OpsAgent tests.

The point of these is not that `Agent(...)` works — that is Microsoft's test
suite. It is that the *same* agent definition comes out identical no matter
which provider is configured, which is the claim the session is built on.
"""

from __future__ import annotations

import pytest

from _support import skip_if_missing
from agent import (
    OPSAGENT_DESCRIPTION,
    OPSAGENT_INSTRUCTIONS,
    OPSAGENT_NAME,
    create_ops_agent,
)
from config import API_KEY_VAR, BASE_URL_VAR, MODEL_VAR, PROVIDER_VAR, ConfigError, Settings
from providers import PROVIDERS, create_chat_client
from tools import OPSAGENT_TOOLS

#: Providers that build offline from an API key alone, used to prove the agent
#: is indifferent to which one is selected.
SWAPPABLE = [
    ("google", "GeminiChatClient", "gemini-2.5-flash"),
    ("openai", "OpenAIChatClient", "gpt-4o-mini"),
    ("anthropic", "AnthropicClient", "claude-sonnet-4-5"),
]


def _tool_names(agent) -> list[str]:
    return [tool.name for tool in agent.default_options["tools"]]


@pytest.fixture
def agent():
    """OpsAgent on a throwaway client, so no test depends on a real provider."""
    client = create_chat_client(Settings("openai", api_key="fake", model="gpt-4o-mini"))
    return create_ops_agent(client)


def test_agent_identity(agent):
    assert agent.name == OPSAGENT_NAME
    assert agent.description == OPSAGENT_DESCRIPTION
    assert "OpsAgent" in agent.default_options["instructions"]


def test_agent_carries_every_tool(agent):
    assert _tool_names(agent) == [tool.name for tool in OPSAGENT_TOOLS]


@pytest.mark.parametrize(("provider", "client_class", "model"), SWAPPABLE)
def test_same_agent_on_every_provider(
    provider: str, client_class: str, model: str, monkeypatch: pytest.MonkeyPatch
):
    """
    Swap the model, keep the agent.

    Only `LLM_PROVIDER` and friends change between these runs. The agent's name,
    instructions and tools must come out byte-identical, because nothing in
    `agent.py` or `tools.py` knows a vendor exists.
    """
    skip_if_missing(PROVIDERS[provider])

    monkeypatch.setenv(PROVIDER_VAR, provider)
    monkeypatch.setenv(API_KEY_VAR, "fake")
    monkeypatch.setenv(MODEL_VAR, model)
    monkeypatch.delenv(BASE_URL_VAR, raising=False)

    # load=False so a developer's real .env cannot decide the outcome.
    built = create_ops_agent(create_chat_client(Settings.from_env(load=False)))

    assert type(built.client).__name__ == client_class
    assert built.name == OPSAGENT_NAME
    assert built.default_options["instructions"] == OPSAGENT_INSTRUCTIONS
    assert _tool_names(built) == [tool.name for tool in OPSAGENT_TOOLS]


def test_unconfigured_provider_fails_with_a_readable_message(monkeypatch: pytest.MonkeyPatch):
    """Building the agent surfaces the config error rather than a traceback."""
    monkeypatch.setenv(PROVIDER_VAR, "openai")

    with pytest.raises(ConfigError) as err:
        create_ops_agent()

    assert API_KEY_VAR in str(err.value)


def test_overrides_are_respected():
    client = create_chat_client(Settings("openai", api_key="fake", model="gpt-4o-mini"))
    built = create_ops_agent(client, tools=[], instructions="Say only 'ok'.")

    assert built.default_options["instructions"] == "Say only 'ok'."
    assert not built.default_options.get("tools")


def test_default_tool_list_is_not_shared_between_agents():
    """
    A caller mutating one agent's tools must not affect the next agent.

    `create_ops_agent` copies OPSAGENT_TOOLS for exactly this reason.
    """
    client = create_chat_client(Settings("openai", api_key="fake", model="gpt-4o-mini"))
    first = create_ops_agent(client)
    first.default_options["tools"].clear()

    second = create_ops_agent(client)
    assert _tool_names(second) == [tool.name for tool in OPSAGENT_TOOLS]
