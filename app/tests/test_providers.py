"""
Provider factory tests.

The claim this file defends is the thesis of the workshop: every supported
provider resolves to a working chat client from the same four variables, with no
network and no vendor-specific code path outside `providers.py`.

It also pins the two rules that keep the factory honest:

  * Nothing is guessed. Every provider requires an explicit `LLM_MODEL`, so a
    default model name cannot rot into a confusing 404 months from now.
  * Nothing fails silently. Every failure names the variable or package to fix.
"""

from __future__ import annotations

import pytest

import providers
from _support import skip_if_missing
from config import (
    API_KEY_VAR,
    BASE_URL_VAR,
    MODEL_VAR,
    PROVIDER_VAR,
    ConfigError,
    Settings,
    normalise_provider,
)
from providers import (
    PROVIDERS,
    create_chat_client,
    get_spec,
    load_client_class,
    missing_variables,
    provider_keys,
)

#: A fully configured `Settings` for each provider, using fake credentials.
#: Values are shaped like the real thing so the assertions stay meaningful.
COMPLETE: dict[str, Settings] = {
    "google": Settings("google", api_key="fake", model="gemini-2.5-flash"),
    "openai": Settings("openai", api_key="fake", model="gpt-4o-mini"),
    "azure-openai": Settings(
        "azure-openai", api_key="fake", model="my-deployment", base_url="https://x.openai.azure.com"
    ),
    "openai-compatible": Settings(
        "openai-compatible", api_key="fake", model="llama-3.3-70b", base_url="https://api.groq.com/openai/v1"
    ),
    "anthropic": Settings("anthropic", api_key="fake", model="claude-sonnet-4-5"),
    "ollama": Settings("ollama", model="llama3.2"),
    "foundry": Settings("foundry", model="gpt-4o-mini", base_url="https://p.services.ai.azure.com"),
    "foundry-local": Settings("foundry-local", model="phi-4-mini"),
    "bedrock": Settings("bedrock", model="anthropic.claude-sonnet-4-5-20250929-v1:0"),
}

#: `FoundryLocalClient` starts the Foundry Local runtime in its constructor, so
#: it cannot be built on a machine that does not have that runtime installed.
#: Everything this project owns is still covered — the class is resolved in
#: `test_client_class_resolves`; only the vendor's own bootstrap is skipped.
NEEDS_LOCAL_RUNTIME = {"foundry-local"}

BUILDABLE = sorted(set(PROVIDERS) - NEEDS_LOCAL_RUNTIME)
ALL_KEYS = sorted(PROVIDERS)


# ---------------------------------------------------------------------------
# The registry itself
# ---------------------------------------------------------------------------


def test_fixtures_cover_every_provider():
    """A new provider must arrive with a test fixture, not slip through."""
    assert set(COMPLETE) == set(PROVIDERS)


@pytest.mark.parametrize("key", ALL_KEYS)
def test_keys_are_canonical(key: str):
    """Registry keys must already be in the form `normalise_provider` produces."""
    assert normalise_provider(key) == key


@pytest.mark.parametrize("key", ALL_KEYS)
def test_no_provider_defaults_the_model(key: str):
    """
    Every provider requires an explicit model.

    Hardcoding a default is tempting and always ages badly: provider catalogues
    churn, and a stale default surfaces months later as an unexplained 404.
    """
    assert MODEL_VAR in PROVIDERS[key].requires


@pytest.mark.parametrize("key", ALL_KEYS)
def test_required_variables_are_real_variables(key: str):
    """Guard against a typo in a spec turning into an unsatisfiable requirement."""
    known = {API_KEY_VAR, MODEL_VAR, BASE_URL_VAR}
    spec = PROVIDERS[key]
    assert set(spec.requires) <= known
    assert set(spec.optional) <= known
    assert not (set(spec.requires) & set(spec.optional))


@pytest.mark.parametrize("key", ALL_KEYS)
def test_install_hint_matches_extra(key: str):
    """The command in an error message must be the one that actually helps."""
    spec = PROVIDERS[key]
    assert spec.install == ("uv sync" if spec.extra is None else f"uv sync --extra {spec.extra}")


# ---------------------------------------------------------------------------
# Failing loudly
# ---------------------------------------------------------------------------


def test_unknown_provider_lists_every_supported_value():
    with pytest.raises(ConfigError) as err:
        get_spec("github-models")

    message = str(err.value)
    assert "github-models" in message
    assert PROVIDER_VAR in message
    # The retired provider is the likeliest thing a returning participant types,
    # so the error has to hand them the full menu rather than just say "no".
    for key in PROVIDERS:
        assert key in message


@pytest.mark.parametrize("key", ALL_KEYS)
def test_missing_configuration_names_every_variable(key: str):
    """An unconfigured provider reports all of its required variables at once."""
    spec = PROVIDERS[key]
    with pytest.raises(ConfigError) as err:
        create_chat_client(Settings(key))

    message = str(err.value)
    for var in spec.requires:
        assert var in message, f"{key} did not name {var}"
    assert missing_variables(spec, Settings(key)) == list(spec.requires)


def test_partial_configuration_names_only_what_is_missing():
    """Half-configured is the common case, and the worst one to guess about."""
    partial = Settings("azure-openai", api_key="fake", model="my-deployment")

    assert missing_variables(PROVIDERS["azure-openai"], partial) == [BASE_URL_VAR]

    with pytest.raises(ConfigError) as err:
        create_chat_client(partial)

    message = str(err.value)
    assert BASE_URL_VAR in message
    assert "Already set" in message
    assert API_KEY_VAR in message.split("Already set")[1]


def test_blank_value_counts_as_missing(monkeypatch: pytest.MonkeyPatch):
    """`LLM_API_KEY=` in a .env is an unfilled placeholder, not a credential."""
    monkeypatch.setenv(PROVIDER_VAR, "openai")
    monkeypatch.setenv(API_KEY_VAR, "   ")
    monkeypatch.setenv(MODEL_VAR, "gpt-4o-mini")

    settings = Settings.from_env(load=False)
    assert settings.api_key is None

    with pytest.raises(ConfigError, match=API_KEY_VAR):
        create_chat_client(settings)


def test_missing_package_gives_the_uv_command(monkeypatch: pytest.MonkeyPatch):
    """A provider whose package is absent must name the command that installs it."""

    def missing(name: str):
        raise ModuleNotFoundError(f"No module named {name!r}")

    monkeypatch.setattr(providers.importlib, "import_module", missing)

    with pytest.raises(ConfigError) as err:
        load_client_class(PROVIDERS["anthropic"])

    message = str(err.value)
    assert "agent-framework-anthropic" in message
    assert "uv sync --extra anthropic" in message


def test_lazy_stub_package_gives_the_uv_command(monkeypatch: pytest.MonkeyPatch):
    """
    The trap this project actually hits.

    `import agent_framework.anthropic` succeeds without the provider package
    installed — core registers a stub that only raises when a class is read off
    it. If the guard covered the import alone it would catch nothing here, and
    the participant would be told to `pip install` into a uv project.
    """

    class LazyStub:
        def __getattr__(self, name: str):
            raise ModuleNotFoundError(
                "The 'agent-framework-anthropic' package is not installed, "
                "please do `pip install agent-framework-anthropic`"
            )

    monkeypatch.setattr(providers.importlib, "import_module", lambda name: LazyStub())

    with pytest.raises(ConfigError) as err:
        load_client_class(PROVIDERS["anthropic"])

    assert "uv sync --extra anthropic" in str(err.value)


def test_provider_is_required(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv(PROVIDER_VAR, raising=False)
    with pytest.raises(ConfigError, match=PROVIDER_VAR):
        Settings.from_env(load=False)


@pytest.mark.parametrize("written", ["Azure_OpenAI", " AZURE-OPENAI ", "azure_openai"])
def test_provider_spelling_variants_resolve(written: str, monkeypatch: pytest.MonkeyPatch):
    """Case and separator slips shouldn't cost a participant five minutes."""
    monkeypatch.setenv(PROVIDER_VAR, written)
    assert Settings.from_env(load=False).provider == "azure-openai"


# ---------------------------------------------------------------------------
# Resolving and building — the actual claim
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("key", ALL_KEYS)
def test_client_class_resolves(key: str):
    """The class named in each spec exists at the module path the spec gives."""
    spec = PROVIDERS[key]
    skip_if_missing(spec)

    client_class = load_client_class(spec)
    assert isinstance(client_class, type)
    assert client_class.__name__ == spec.client


@pytest.mark.parametrize("key", BUILDABLE)
def test_builds_a_client_offline(key: str):
    """
    The headline test: same four variables in, a live client object out, for
    every provider, with sockets blocked by the `no_network` fixture.
    """
    spec = PROVIDERS[key]
    skip_if_missing(spec)

    client = create_chat_client(COMPLETE[key])
    assert type(client).__name__ == spec.client


def test_openai_family_shares_one_client_class():
    """
    Three providers, one class — the cheapest illustration of the thesis.

    OpenAI, Azure OpenAI and every OpenAI-compatible endpoint differ only by the
    arguments this factory passes.
    """
    family = ["openai", "azure-openai", "openai-compatible"]
    classes = {load_client_class(PROVIDERS[key]) for key in family}
    assert len(classes) == 1


def test_provider_keys_matches_registry():
    assert provider_keys() == tuple(PROVIDERS)
