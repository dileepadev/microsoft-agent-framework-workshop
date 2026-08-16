"""
Shared test helpers.

Participants install only the provider they use, so the suite has to tell
"this provider is broken" apart from "this provider isn't installed here".
"""

from __future__ import annotations

import importlib

import pytest

from providers import ProviderSpec


def provider_installed(spec: ProviderSpec) -> bool:
    """
    Whether this provider's packages are usable in this environment.

    Neither obvious shortcut works. `find_spec("azure.identity")` *raises* when
    the parent `azure` package is absent rather than returning None, and
    `find_spec("agent_framework.anthropic")` *succeeds* without the provider
    package because core registers a lazy stub. Only reaching the class settles
    it, so this mirrors what `load_client_class` does.

    A wrong class name in a spec raises AttributeError here and fails the test
    rather than skipping it, which is the correct outcome.
    """
    try:
        for name in spec.modules[1:]:
            importlib.import_module(name)
        module = importlib.import_module(spec.module)
        getattr(module, spec.client)
    except ImportError:
        return False
    return True


def skip_if_missing(spec: ProviderSpec) -> None:
    """Skip the calling test, naming the command that would enable it."""
    if not provider_installed(spec):
        pytest.skip(f"{spec.package} not installed — run `{spec.install}`")
