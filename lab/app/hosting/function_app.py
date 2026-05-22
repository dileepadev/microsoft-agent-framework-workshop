# Copyright (c) Microsoft. All rights reserved.

"""OpsAgent hosted as an Azure Function via the Durable Extension for Agent Framework.

Components used:
- OpenAIChatCompletionClient   — GitHub Models (gpt-4o-mini)
- @tool decorator              — Module 4 tools (health check, checklist, diagnostics)
- MCPStreamableHTTPTool        — Module 5 Microsoft Learn MCP
- InMemoryHistoryProvider      — Module 6 multi-turn history
- AgentFunctionApp             — Durable extension HTTP endpoint registration

Run locally:
    cd lab/app/hosting
    func start

Invoke:
    curl -i -X POST http://localhost:7071/api/agents/OpsAgent/run \\
         -H "Content-Type: text/plain" \\
         -d "Check the health of App Service in East US."
"""

import os
import random
from datetime import datetime, timezone
from typing import Annotated, Any

from agent_framework import Agent, InMemoryHistoryProvider, MCPStreamableHTTPTool, tool
from agent_framework.azure import AgentFunctionApp
from agent_framework.openai import OpenAIChatCompletionClient
from dotenv import load_dotenv
from openai import AsyncOpenAI
from pydantic import Field

load_dotenv()

GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]
GITHUB_MODEL = os.environ["GITHUB_MODEL"]
GITHUB_BASE_URL = "https://models.github.ai/inference"


# ---------------------------------------------------------------------------
# Module 4 — Tools
# ---------------------------------------------------------------------------

# NOTE: approval_mode="never_require" is for sample brevity.
# Use "always_require" in production for user confirmation before tool execution.


@tool(approval_mode="never_require")
def check_azure_service_health(
    service: Annotated[
        str,
        Field(
            description="The Azure service name to check, e.g. 'App Service', 'AKS'."
        ),
    ],
    region: Annotated[
        str,
        Field(description="Azure region, e.g. 'East US', 'West Europe'."),
    ] = "East US",
) -> str:
    """Check the health status of an Azure service in a given region."""
    statuses = ["Healthy", "Degraded", "Under investigation"]
    weights = [0.8, 0.15, 0.05]
    status = random.choices(statuses, weights=weights)[0]
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    return f"Azure {service} in {region}: {status}. Last checked: {timestamp}"


@tool(approval_mode="never_require")
def get_deployment_checklist(
    service_type: Annotated[
        str,
        Field(
            description="Azure service type, e.g. 'Container App', 'AKS', 'App Service'."
        ),
    ],
) -> str:
    """Return a deployment readiness checklist for the given Azure service type."""
    checklists: dict[str, list[str]] = {
        "container app": [
            "Confirm container image is pushed to ACR",
            "Set AZURE_RESOURCE_GROUP and AZURE_LOCATION environment variables",
            "Run: az containerapp up --name <app> --image <registry>/<image>:<tag>",
            "Configure ingress (external/internal) and target port",
            "Check replica count and autoscaling rules",
        ],
        "aks": [
            "Ensure kubectl is configured: az aks get-credentials --resource-group <rg> --name <cluster>",
            "Validate manifests with: kubectl apply --dry-run=client -f <file>",
            "Check node pool capacity and resource quotas",
            "Confirm image pull secrets for private registry",
            "Apply RBAC and network policies before deployment",
        ],
        "app service": [
            "Verify App Service plan tier meets workload requirements",
            "Set app settings via: az webapp config appsettings set",
            "Enable deployment slot for zero-downtime swap",
            "Configure health check endpoint under Settings > Health check",
            "Deploy using: az webapp deploy or a GitHub Actions workflow",
        ],
        "function app": [
            "Set storage account connection string (AzureWebJobsStorage)",
            "Choose Consumption, Premium, or Dedicated hosting plan",
            "Configure FUNCTIONS_WORKER_RUNTIME to match your language runtime",
            "Deploy with: func azure functionapp publish <app-name>",
            "Enable Application Insights for monitoring and alerting",
        ],
    }
    key = service_type.lower()
    for k, items in checklists.items():
        if k in key:
            checklist = "\n".join(f"  - {item}" for item in items)
            return f"Deployment checklist for {service_type}:\n{checklist}"
    return (
        f"Generic checklist for {service_type}:\n"
        "  - Review the official Azure documentation for this service\n"
        "  - Validate resource quotas in your subscription\n"
        "  - Configure monitoring and alerts before going live\n"
        "  - Test the deployment in a staging environment first"
    )


@tool(approval_mode="never_require")
def diagnose_error(
    error_code: Annotated[
        str,
        Field(description="HTTP status code or Azure error code, e.g. '503', '429'."),
    ],
    service: Annotated[
        str,
        Field(description="Azure service reporting the error."),
    ] = "unknown",
) -> str:
    """Return a diagnosis and suggested resolution for a given error code."""
    diagnoses: dict[str, str] = {
        "503": "Service Unavailable — check instance count, CPU/memory limits, and health-check endpoint.",
        "429": "Too Many Requests — reduce call rate or increase RU/s quota.",
        "401": "Unauthorized — verify API key, managed identity assignment, or RBAC role.",
        "500": "Internal Server Error — inspect application logs and review recent deployments.",
    }
    return diagnoses.get(
        error_code,
        f"Error {error_code} on {service}: consult Azure Monitor and service logs.",
    )


# ---------------------------------------------------------------------------
# Module 5 — MCP (Microsoft Learn)
# ---------------------------------------------------------------------------

learn_mcp = MCPStreamableHTTPTool(
    name="Microsoft Learn MCP",
    url="https://learn.microsoft.com/api/mcp",
    approval_mode="never_require",
)


# ---------------------------------------------------------------------------
# Agent factory
# ---------------------------------------------------------------------------


def _create_ops_agent() -> Any:
    """Create OpsAgent wired with all Module 4–6 features."""
    client = OpenAIChatCompletionClient(
        model=GITHUB_MODEL,
        async_client=AsyncOpenAI(
            api_key=GITHUB_TOKEN,
            base_url=GITHUB_BASE_URL,
        ),
    )
    return Agent(
        client=client,
        name="OpsAgent",
        description="OpsAgent is an AI-powered operations and engineering assistant.",
        instructions=(
            "You are OpsAgent, an AI-powered operations and engineering assistant. "
            "Help developers and cloud engineers troubleshoot issues, retrieve documentation, "
            "analyze systems, and automate operational workflows. "
            "Use the available tools when relevant. Keep responses concise, actionable, and practical."
        ),
        tools=[
            check_azure_service_health,
            get_deployment_checklist,
            diagnose_error,
            learn_mcp,
        ],
        context_providers=[
            InMemoryHistoryProvider(load_messages=True),
        ],
    )


# ---------------------------------------------------------------------------
# Azure Functions app — exposes OpsAgent via HTTP + durable state management
# ---------------------------------------------------------------------------

app = AgentFunctionApp(
    agents=[_create_ops_agent()], enable_health_check=True, max_poll_retries=50
)

"""
Expected output after running `func start` and invoking the endpoint:

    HTTP/1.1 200 OK
    Content-Type: text/plain; charset=utf-8
    x-ms-thread-id: <guid>

    Azure App Service in East US: Healthy. Last checked: 2026-05-22 10:00 UTC

Pass the returned x-ms-thread-id as ?thread_id=<guid> on subsequent requests
to continue the same conversation (Module 6 multi-turn history).
"""
