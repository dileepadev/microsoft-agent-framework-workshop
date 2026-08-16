"""
Tool tests.

Tools are ordinary Python functions, and testing them like ordinary Python
functions is the point — no model, no key, no provider. Whatever OpsAgent is
running on, these return the same strings.
"""

from __future__ import annotations

import pytest

from tools import (
    OPSAGENT_TOOLS,
    check_azure_service_health,
    diagnose_error,
    get_deployment_checklist,
)


def test_every_tool_is_named_and_described():
    """The model picks tools from these strings, so both must be present."""
    for tool in OPSAGENT_TOOLS:
        assert tool.name
        assert tool.description, f"{tool.name} has no description for the model to read"


def test_health_check_labels_its_output_as_simulated():
    """
    Canned data must announce itself.

    An agent that reports a made-up Azure status as fact is worse than one with
    no tools at all, and a room of participants should be able to tell which is
    which from the output.
    """
    result = check_azure_service_health("App Service", "West Europe")

    assert "[simulated]" in result
    assert "App Service" in result
    assert "West Europe" in result


def test_health_check_defaults_its_region():
    assert "East US" in check_azure_service_health("Cosmos DB")


@pytest.mark.parametrize(
    ("service_type", "expected"),
    [
        ("Container App", "az containerapp up"),
        ("AKS", "az aks get-credentials"),
        ("App Service", "az webapp"),
        ("Function App", "func azure functionapp publish"),
        # Matching is substring-based, so real-world phrasing still lands.
        ("azure container app (production)", "az containerapp up"),
    ],
)
def test_checklist_matches_known_service_types(service_type: str, expected: str):
    assert expected in get_deployment_checklist(service_type)


def test_checklist_falls_back_without_pretending():
    """An unknown service gets general advice, not invented specifics."""
    result = get_deployment_checklist("Quantum Workspace")

    assert "No specific checklist" in result
    assert "Quantum Workspace" in result


@pytest.mark.parametrize(
    ("code", "expected"),
    [
        ("429", "Throttling"),
        ("503", "Service Unavailable"),
        ("403", "Forbidden"),
        ("ResourceNotFound", "Resource Not Found"),
        ("resource not found", "Resource Not Found"),
        ("Timeout", "Request Timeout"),
    ],
)
def test_diagnose_known_errors(code: str, expected: str):
    result = diagnose_error(code, "Cosmos DB")

    assert expected in result
    assert "Cosmos DB" in result
    assert "1." in result, "guidance should be numbered steps"


def test_diagnose_unknown_error_says_so():
    result = diagnose_error("ITEAPOT", "App Service")

    assert "No specific guidance" in result
    assert "ITEAPOT" in result


def test_diagnose_defaults_the_service():
    assert "unknown" in diagnose_error("429")
