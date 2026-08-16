"""
Shared test fixtures.

Two guarantees hold for every test in this package:

  * The developer's real `app/.env` cannot influence a result.
  * Nothing opens a socket.

Both are enforced automatically rather than by convention, because a provider
test that quietly depends on a key in someone's `.env` passes on their laptop
and fails in CI.
"""

from __future__ import annotations

import socket

import pytest

from config import API_KEY_VAR, BASE_URL_VAR, MODEL_VAR, PROVIDER_VAR

#: Variables that would otherwise leak in from the shell or a loaded .env.
LEAKY_VARS = (
    PROVIDER_VAR,
    API_KEY_VAR,
    MODEL_VAR,
    BASE_URL_VAR,
    # Provider SDKs read their own variables too, and several will happily
    # succeed on those alone — masking a factory that passed nothing.
    "GEMINI_API_KEY",
    "GOOGLE_API_KEY",
    "OPENAI_API_KEY",
    "ANTHROPIC_API_KEY",
    "AZURE_OPENAI_API_KEY",
    "AZURE_OPENAI_ENDPOINT",
    "OLLAMA_HOST",
    "OLLAMA_MODEL",
    "FOUNDRY_PROJECT_ENDPOINT",
    "FOUNDRY_MODEL",
    "FOUNDRY_LOCAL_MODEL",
)


@pytest.fixture(autouse=True)
def clean_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Start every test from an environment with no provider configuration."""
    for var in LEAKY_VARS:
        monkeypatch.delenv(var, raising=False)

    # Bedrock resolves region and credentials through the AWS chain rather than
    # through LLM_*, so it needs plausible values to construct at all. These are
    # obvious fakes — the no_network fixture guarantees they are never used.
    monkeypatch.setenv("BEDROCK_REGION", "us-east-1")
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "testing")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "testing")
    monkeypatch.setenv("AWS_SESSION_TOKEN", "testing")
    monkeypatch.setenv("AWS_EC2_METADATA_DISABLED", "true")


@pytest.fixture(autouse=True)
def no_network(monkeypatch: pytest.MonkeyPatch) -> None:
    """Turn any outbound connection into a test failure.

    Building a chat client must be pure local object construction. If that ever
    stops being true, participants would need a live key just to import the app,
    so the guarantee is worth asserting rather than assuming.
    """

    def blocked(*args: object, **kwargs: object) -> None:
        raise AssertionError(
            "A test tried to open a network connection. Building a chat client "
            "must not require the network."
        )

    monkeypatch.setattr(socket.socket, "connect", blocked)
    monkeypatch.setattr(socket.socket, "connect_ex", blocked)
    monkeypatch.setattr(socket, "create_connection", blocked)
