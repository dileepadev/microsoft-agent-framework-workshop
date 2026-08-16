"""
Triage workflow tests.

`classify_severity` is the reason this workflow exists, so it gets the bulk of
the coverage: it is pure, deterministic, and needs no model. That is exactly the
argument for putting routing in a workflow step rather than a prompt — you can
test it like this.
"""

from __future__ import annotations

import pytest

from agent_framework import Workflow

from config import Settings
from providers import create_chat_client
from workflow import CRITICAL, HIGH, INFO, build_triage_workflow, classify_severity


@pytest.mark.parametrize(
    ("query", "expected"),
    [
        ("Production is down", CRITICAL),
        ("we have a full outage in West Europe", CRITICAL),
        ("the deployment failed", CRITICAL),
        ("P1 incident on checkout", CRITICAL),
        ("seeing a spike in 500 error responses", HIGH),
        ("the API is slow this morning", HIGH),
        ("cluster is degraded", HIGH),
        ("how do I deploy a container app?", INFO),
        ("what is the difference between AKS and ACA?", INFO),
    ],
)
def test_severity_classification(query: str, expected: str):
    assert classify_severity(query) == expected


def test_classification_is_case_insensitive():
    assert classify_severity("PRODUCTION IS DOWN") == CRITICAL


def test_critical_outranks_high():
    """A message with both signals is the dangerous one — it must not read HIGH."""
    assert classify_severity("slow responses, then the service went down") == CRITICAL


def test_classification_needs_no_model():
    """
    Routing is deterministic and free.

    The no_network fixture is what makes this meaningful: severity is decided
    without a single token being spent.
    """
    assert classify_severity("everything crashed") == CRITICAL


def test_builds_a_workflow_offline():
    client = create_chat_client(Settings("openai", api_key="fake", model="gpt-4o-mini"))
    assert isinstance(build_triage_workflow(client), Workflow)


def test_each_build_is_a_fresh_instance():
    """Workflows carry run state, so handing the same one to two callers is a bug."""
    client = create_chat_client(Settings("openai", api_key="fake", model="gpt-4o-mini"))
    assert build_triage_workflow(client) is not build_triage_workflow(client)
