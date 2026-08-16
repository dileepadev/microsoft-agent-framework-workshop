"""
Configuration — the four variables that decide which model OpsAgent talks to.

The whole workshop rests on one idea: swapping the model should be a config
change, not a rewrite. That promise only holds if configuration is small, so the
entire contract is four variables:

    LLM_PROVIDER    which provider to use          (always required)
    LLM_API_KEY     the credential                 (most providers)
    LLM_MODEL       the model or deployment id     (always required)
    LLM_BASE_URL    the endpoint                   (some providers)

`providers.py` decides which of those a given provider actually needs.

Two rules this module exists to enforce:

  1. `.env` is loaded explicitly. Agent Framework used to pick `.env` up on its
     own and no longer does, so without `load_env()` nothing below works.
  2. Missing configuration fails at startup, naming the variable to set. A
     workshop participant should never have to read a stack trace to learn they
     forgot to paste an API key.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import find_dotenv, load_dotenv

# The .env this project ships with, next to the code rather than at the repo
# root, because app/ is its own environment.
ENV_FILE = Path(__file__).resolve().parent / ".env"

PROVIDER_VAR = "LLM_PROVIDER"
API_KEY_VAR = "LLM_API_KEY"
MODEL_VAR = "LLM_MODEL"
BASE_URL_VAR = "LLM_BASE_URL"

#: Maps an environment variable name to the `Settings` field that holds it.
VAR_FIELDS: dict[str, str] = {
    API_KEY_VAR: "api_key",
    MODEL_VAR: "model",
    BASE_URL_VAR: "base_url",
}


class ConfigError(RuntimeError):
    """
    Raised when the environment cannot produce a usable configuration.

    Always carries a message naming the exact variable to set — that is the
    entire point of the class.
    """


def _clean(value: str | None) -> str | None:
    """Treat whitespace and the empty string as 'not set'.

    `LLM_API_KEY=` in a .env file yields `""`, not `None`. Without this, an
    unfilled placeholder would sail past the required-variable check and fail
    much later as an authentication error.
    """
    if value is None:
        return None
    stripped = value.strip()
    return stripped or None


def normalise_provider(value: str) -> str:
    """Fold provider spelling variants onto the canonical key.

    Accepts `Azure_OpenAI`, `azure-openai` and `AZURE-OPENAI` alike, so a
    participant loses no time to a typo that was never really an error.
    """
    return value.strip().lower().replace("_", "-")


def load_env(path: str | Path | None = None, *, override: bool = False) -> Path | None:
    """
    Load `.env` into `os.environ` and return the file used, or None if none was
    found.

    Real environment variables win over the file unless `override=True`. That is
    what you want on a deployed host, where the platform injects configuration
    and there is no `.env` at all.
    """
    env_file = Path(path) if path else ENV_FILE
    if env_file.is_file():
        load_dotenv(env_file, override=override)
        return env_file

    # Nothing beside the code — fall back to any .env at or above the working
    # directory, which is how most people run this from a shell.
    discovered = find_dotenv(usecwd=True)
    if discovered:
        load_dotenv(discovered, override=override)
        return Path(discovered)
    return None


@dataclass(frozen=True)
class Settings:
    """The resolved provider configuration for a single agent."""

    provider: str
    api_key: str | None = None
    model: str | None = None
    base_url: str | None = None

    @classmethod
    def from_env(cls, *, load: bool = True) -> Settings:
        """Read settings from the environment, loading `.env` first by default."""
        if load:
            load_env()

        provider = _clean(os.getenv(PROVIDER_VAR))
        if not provider:
            # Deliberately raised before anything else: without a provider there
            # is no way to say which other variables matter.
            raise ConfigError(
                f"{PROVIDER_VAR} is not set.\n\n"
                f"Copy app/.env.example to app/.env and set {PROVIDER_VAR} to the "
                f"provider you have a key for.\n"
                f"Run `python -m providers` to list the supported values."
            )

        return cls(
            provider=normalise_provider(provider),
            api_key=_clean(os.getenv(API_KEY_VAR)),
            model=_clean(os.getenv(MODEL_VAR)),
            base_url=_clean(os.getenv(BASE_URL_VAR)),
        )

    def get(self, var: str) -> str | None:
        """Look a value up by its environment variable name."""
        field = VAR_FIELDS.get(var)
        if field is None:
            raise KeyError(f"{var} is not one of {', '.join(VAR_FIELDS)}")
        return getattr(self, field)
