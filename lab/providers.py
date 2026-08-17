"""
The provider factory — one agent core, any model behind it.

Ported from `app/providers.py` because `lab/` is its own `uv` project and
shares nothing with `app/`. The registry, the builders and the fail-loud
messages are identical; only the paths in the error text point at `lab/`
instead of `app/`.

    from providers import create_chat_client
    client = create_chat_client()          # reads .env

Every exercise is written once against that client and never changes when the
provider does. Adding a provider means adding one `ProviderSpec` below —
nothing else moves.

Run `python -m providers` to print the supported providers and what each needs.
"""

from __future__ import annotations

import importlib
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from config import API_KEY_VAR, BASE_URL_VAR, MODEL_VAR, PROVIDER_VAR, ConfigError, Settings

# ---------------------------------------------------------------------------
# Spec
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ProviderSpec:
    """
    Everything the factory knows about one provider.

    Deliberately data, not code: the registry can be inspected, printed and
    tested without importing a single vendor SDK or touching the network.
    """

    key: str
    label: str
    #: Modules that must import before `build` can run. The first one holds the
    #: client class; any others are transitive requirements such as a credential
    #: library. All are checked up front so a missing package is reported as an
    #: install command rather than an ImportError from deep inside a builder.
    modules: tuple[str, ...]
    client: str
    package: str
    #: The optional-dependency extra that installs `package`, or None when it
    #: is already a base dependency.
    extra: str | None
    #: Required environment variables, mapped to the hint shown when unset.
    requires: dict[str, str]
    build: Callable[[type[Any], Settings], Any]
    notes: str = ""
    #: Variables that change behaviour but are not required.
    optional: dict[str, str] = field(default_factory=dict)

    @property
    def module(self) -> str:
        """The module holding the client class."""
        return self.modules[0]

    @property
    def install(self) -> str:
        """The command that makes this provider importable."""
        if self.extra is None:
            return "uv sync"
        return f"uv sync --extra {self.extra}"


# ---------------------------------------------------------------------------
# Builders
#
# One per provider, each taking the resolved client class and the settings.
# Signatures below were taken from the installed packages, not from the docs —
# `agent_framework.amazon` in particular is not where the documentation implies.
# ---------------------------------------------------------------------------


def _build_openai(client: type[Any], s: Settings) -> Any:
    return client(model=s.model, api_key=s.api_key)


def _build_azure_openai(client: type[Any], s: Settings) -> Any:
    # `azure_endpoint` is the explicit Azure routing signal. Since 1.0.0rc6 the
    # generic OpenAI clients no longer drift to Azure just because AZURE_OPENAI_*
    # variables happen to be present, so passing it is what selects Azure.
    return client(model=s.model, api_key=s.api_key, azure_endpoint=s.base_url)


def _build_openai_compatible(client: type[Any], s: Settings) -> Any:
    return client(model=s.model, api_key=s.api_key, base_url=s.base_url)


def _build_gemini(client: type[Any], s: Settings) -> Any:
    return client(model=s.model, api_key=s.api_key)


def _build_anthropic(client: type[Any], s: Settings) -> Any:
    return client(model=s.model, api_key=s.api_key, base_url=s.base_url)


def _build_ollama(client: type[Any], s: Settings) -> Any:
    # No API key: Ollama serves on localhost. `host` defaults to
    # http://localhost:11434 when LLM_BASE_URL is unset.
    return client(model=s.model, host=s.base_url)


def _build_foundry(client: type[Any], s: Settings) -> Any:
    # Entra ID rather than an API key, so `az login` is the credential step.
    from azure.identity import AzureCliCredential

    return client(
        project_endpoint=s.base_url,
        model=s.model,
        credential=AzureCliCredential(),
    )


def _build_foundry_local(client: type[Any], s: Settings) -> Any:
    # Downloads and starts the model on first use, which is why the first run
    # takes minutes and later ones are instant.
    return client(model=s.model)


def _build_bedrock(client: type[Any], s: Settings) -> Any:
    # Region and credentials come from the standard AWS chain (BEDROCK_REGION,
    # AWS_*, ~/.aws/config, instance roles) rather than from LLM_* variables.
    # Bending AWS auth into this factory's four variables would break every AWS
    # deployment story participants already have.
    return client(model=s.model)


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

_MODEL_HINT = "the model id to use"

PROVIDERS: dict[str, ProviderSpec] = {
    spec.key: spec
    for spec in (
        ProviderSpec(
            key="google",
            label="Google AI Studio (Gemini)",
            modules=("agent_framework.gemini",),
            client="GeminiChatClient",
            package="agent-framework-gemini",
            extra=None,
            build=_build_gemini,
            requires={
                API_KEY_VAR: "a Google AI Studio API key from aistudio.google.com/apikey",
                MODEL_VAR: "a Gemini model id, e.g. gemini-2.5-flash",
            },
            notes="The workshop default — generous free tier, no card required.",
        ),
        ProviderSpec(
            key="openai",
            label="OpenAI",
            modules=("agent_framework.openai",),
            client="OpenAIChatClient",
            package="agent-framework-openai",
            extra=None,
            build=_build_openai,
            requires={
                API_KEY_VAR: "an OpenAI API key from platform.openai.com/api-keys",
                MODEL_VAR: _MODEL_HINT,
            },
        ),
        ProviderSpec(
            key="azure-openai",
            label="Azure OpenAI",
            modules=("agent_framework.openai",),
            client="OpenAIChatClient",
            package="agent-framework-openai",
            extra=None,
            build=_build_azure_openai,
            requires={
                API_KEY_VAR: "an Azure OpenAI resource key",
                MODEL_VAR: "your DEPLOYMENT name, which is not always the model name",
                BASE_URL_VAR: "https://<your-resource>.openai.azure.com",
            },
            notes="Same client class as OpenAI — only the endpoint differs.",
        ),
        ProviderSpec(
            key="openai-compatible",
            label="Any OpenAI-compatible endpoint",
            modules=("agent_framework.openai",),
            client="OpenAIChatClient",
            package="agent-framework-openai",
            extra=None,
            build=_build_openai_compatible,
            requires={
                API_KEY_VAR: "the provider's API key",
                MODEL_VAR: _MODEL_HINT,
                BASE_URL_VAR: "the provider's OpenAI-compatible base URL",
            },
            notes=(
                "The catch-all: OpenRouter, Groq, Cerebras, Together, Fireworks, "
                "DeepSeek, xAI, LM Studio, vLLM — anything OpenAI-shaped."
            ),
        ),
        ProviderSpec(
            key="anthropic",
            label="Anthropic (Claude)",
            modules=("agent_framework.anthropic",),
            client="AnthropicClient",
            package="agent-framework-anthropic",
            extra="anthropic",
            build=_build_anthropic,
            requires={
                API_KEY_VAR: "an Anthropic API key from console.anthropic.com",
                MODEL_VAR: "a Claude model id, e.g. claude-sonnet-4-5",
            },
            optional={BASE_URL_VAR: "an Anthropic-compatible endpoint, e.g. a Foundry deployment"},
        ),
        ProviderSpec(
            key="ollama",
            label="Ollama (local)",
            modules=("agent_framework.ollama",),
            client="OllamaChatClient",
            package="agent-framework-ollama",
            extra=None,
            build=_build_ollama,
            requires={
                MODEL_VAR: "a pulled model that supports tools, e.g. llama3.2 or qwen3:4b",
            },
            optional={BASE_URL_VAR: "the Ollama host (default http://localhost:11434)"},
            notes=(
                "No key, no network. The fallback when conference wifi fails — "
                "note that not every local model can call tools."
            ),
        ),
        ProviderSpec(
            key="foundry",
            label="Microsoft Foundry",
            modules=("agent_framework.foundry", "azure.identity"),
            client="FoundryChatClient",
            package="agent-framework-foundry",
            extra="foundry",
            build=_build_foundry,
            requires={
                MODEL_VAR: "the model deployed in your Foundry project",
                BASE_URL_VAR: "https://<your-project>.services.ai.azure.com",
            },
            notes="Authenticates with `az login`, so no API key is needed.",
        ),
        ProviderSpec(
            key="foundry-local",
            label="Foundry Local",
            modules=("agent_framework.foundry",),
            client="FoundryLocalClient",
            package="agent-framework-foundry-local",
            extra="foundry-local",
            build=_build_foundry_local,
            requires={MODEL_VAR: "a Foundry Local model, e.g. phi-4-mini"},
            notes="Runs Foundry models on this machine. First run downloads the model.",
        ),
        ProviderSpec(
            key="bedrock",
            label="Amazon Bedrock",
            modules=("agent_framework.amazon",),
            client="BedrockChatClient",
            package="agent-framework-bedrock",
            extra="bedrock",
            build=_build_bedrock,
            requires={MODEL_VAR: "a Bedrock model id, e.g. anthropic.claude-sonnet-4-5-20250929-v1:0"},
            notes=(
                "Credentials and region come from the AWS chain (BEDROCK_REGION, "
                f"AWS_*), not from {API_KEY_VAR}."
            ),
        ),
    )
}


# ---------------------------------------------------------------------------
# Lookup and validation
# ---------------------------------------------------------------------------


def provider_keys() -> tuple[str, ...]:
    """Every supported `LLM_PROVIDER` value."""
    return tuple(PROVIDERS)


def get_spec(key: str) -> ProviderSpec:
    """Resolve a provider key, or fail with the full list of valid values."""
    spec = PROVIDERS.get(key)
    if spec is not None:
        return spec

    width = max(len(k) for k in PROVIDERS)
    listing = "\n".join(f"  {k:<{width}}  {s.label}" for k, s in PROVIDERS.items())
    raise ConfigError(
        f"{PROVIDER_VAR}={key!r} is not a supported provider.\n\n"
        f"Supported values:\n{listing}\n\n"
        f"Set {PROVIDER_VAR} in lab/.env to one of the values above."
    )


def missing_variables(spec: ProviderSpec, settings: Settings) -> list[str]:
    """The required variables this provider still needs, in declaration order."""
    return [var for var in spec.requires if not settings.get(var)]


def _check_configured(spec: ProviderSpec, settings: Settings) -> None:
    """Fail with a message that names every variable still missing."""
    missing = missing_variables(spec, settings)
    if not missing:
        return

    width = max(len(var) for var in missing)
    listing = "\n".join(f"  {var:<{width}}  {spec.requires[var]}" for var in missing)
    already = [var for var in spec.requires if settings.get(var)]

    message = (
        f"Provider {spec.key!r} ({spec.label}) is missing required configuration.\n\n"
        f"Set the following in lab/.env:\n{listing}"
    )
    if already:
        message += f"\n\nAlready set: {', '.join(already)}"
    if spec.notes:
        message += f"\n\nNote: {spec.notes}"
    raise ConfigError(message)


def load_client_class(spec: ProviderSpec) -> type[Any]:
    """
    Import the provider's client class.

    Imports are deferred to here so that installing one provider is enough to
    run an exercise. Importing every vendor SDK at module load would make the
    whole factory fail because of a provider nobody in the room is using.

    The `getattr` sits inside the guard deliberately. `import
    agent_framework.anthropic` *succeeds* when agent-framework-anthropic is not
    installed — the core package registers a lazy stub that only raises when a
    class is read off it. Guarding the import alone therefore catches nothing,
    and you would be left with the framework's own advice to run `pip install`,
    which is the wrong command for this uv project.
    """
    try:
        # The client lives in modules[0]; the rest are transitive requirements
        # such as a credential library, imported only to prove they are present.
        for name in spec.modules[1:]:
            importlib.import_module(name)
        module = importlib.import_module(spec.module)
        return getattr(module, spec.client)
    except ImportError as exc:
        raise ConfigError(
            f"Provider {spec.key!r} ({spec.label}) needs the {spec.package} "
            f"package, which is not installed.\n\n"
            f"Install it from lab/:\n  {spec.install}\n\n"
            f"(underlying error: {exc})"
        ) from exc


def create_chat_client(settings: Settings | None = None) -> Any:
    """
    Build the chat client for the configured provider.

    This is the only function in this project that knows a vendor exists.

    Raises:
        ConfigError: unknown provider, missing variable, or missing package —
            always naming what to fix.
    """
    resolved = settings or Settings.from_env()
    spec = get_spec(resolved.provider)
    _check_configured(spec, resolved)
    client_class = load_client_class(spec)
    return spec.build(client_class, resolved)


# ---------------------------------------------------------------------------
# `python -m providers`
# ---------------------------------------------------------------------------


def describe() -> str:
    """A readable table of every provider and what it needs."""
    lines = ["Supported LLM_PROVIDER values", ""]
    for key, spec in PROVIDERS.items():
        lines.append(f"  {key}  —  {spec.label}")
        required = ", ".join(spec.requires) or "nothing"
        lines.append(f"      requires  {required}")
        if spec.optional:
            lines.append(f"      optional  {', '.join(spec.optional)}")
        lines.append(f"      install   {spec.install}")
        if spec.notes:
            lines.append(f"      note      {spec.notes}")
        lines.append("")
    return "\n".join(lines)


if __name__ == "__main__":
    print(describe())
