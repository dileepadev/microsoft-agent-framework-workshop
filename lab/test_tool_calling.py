"""
Module 4 - Test Tool Calling with OpsAgent

Run:
    python test_tool_calling.py
    or
    uv run test_tool_calling.py
"""

import asyncio
import os
import random
from datetime import datetime, timezone
from typing import Annotated

from dotenv import load_dotenv
from openai import AsyncOpenAI
from pydantic import Field

from agent_framework import Agent, tool
from agent_framework.openai import OpenAIChatCompletionClient

load_dotenv()

github_base_url = "https://models.github.ai/inference"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_MODEL = os.getenv("GITHUB_MODEL")

if not GITHUB_TOKEN or not GITHUB_MODEL:
    raise ValueError("GITHUB_TOKEN and GITHUB_MODEL must be set in the .env file")


# ---------------------------------------------------------------------------
# OpsAgent Tools
# ---------------------------------------------------------------------------

# NOTE: approval_mode="never_require" is for sample brevity.
# Use "always_require" in production for user confirmation before tool execution.


@tool(approval_mode="never_require")
def check_azure_service_health(
    service: Annotated[
        str,
        Field(
            description="The Azure service name to check, e.g. 'App Service', 'AKS', 'Cosmos DB'."
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
            description="Azure service type, e.g. 'Container App', 'AKS', 'App Service', 'Function App'."
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
            "Validate Helm chart or manifests with: kubectl apply --dry-run=client -f <file>",
            "Check node pool capacity and resource quotas",
            "Confirm image pull secrets for private registry",
            "Apply RBAC and network policies before deployment",
        ],
        "app service": [
            "Verify App Service plan tier meets workload requirements",
            "Set app settings and connection strings via: az webapp config appsettings set",
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
        Field(
            description="HTTP status code or Azure error code, e.g. '429', '503', 'ResourceNotFound'."
        ),
    ],
    service: Annotated[
        str,
        Field(description="The Azure service or component where the error occurred."),
    ] = "unknown",
) -> str:
    """Diagnose a common error code and return actionable troubleshooting guidance."""
    diagnoses: dict[str, tuple[str, list[str]]] = {
        "429": (
            "Too Many Requests / Throttling",
            [
                "Implement exponential backoff with jitter in your retry logic.",
                "Check the Retry-After response header for the required wait duration.",
                "Review your service tier and consider requesting a quota increase.",
                "For Cosmos DB: monitor RU consumption and scale up provisioned throughput.",
            ],
        ),
        "503": (
            "Service Unavailable",
            [
                "The service may be temporarily overloaded or under maintenance.",
                "Check the Azure Service Health dashboard for active incidents.",
                "Verify health check probes are not timing out prematurely.",
                "Retry with exponential backoff; activate a failover region if configured.",
            ],
        ),
        "resourcenotfound": (
            "Resource Not Found",
            [
                "Confirm the resource name, resource group, and subscription ID are correct.",
                "Ensure the resource has not been deleted or moved to another group.",
                "Check RBAC permissions — you may lack read access to the resource.",
                "Verify the correct Azure region is targeted in your request.",
            ],
        ),
        "403": (
            "Forbidden / Authorization Failure",
            [
                "Verify the managed identity or service principal has the required RBAC roles.",
                "Check that no resource policy or deny assignment is blocking the operation.",
                "Ensure the request includes a valid and non-expired Bearer token.",
            ],
        ),
        "timeout": (
            "Request Timeout",
            [
                "Increase the client-side timeout setting in your SDK or HTTP client.",
                "Check the network path: VNet peering, NSG rules, and private endpoints.",
                "Review CPU and memory pressure on the target service.",
            ],
        ),
    }
    key = error_code.lower().replace(" ", "")
    for k, (title, steps) in diagnoses.items():
        if k in key:
            guidance = "\n".join(f"  {i + 1}. {s}" for i, s in enumerate(steps))
            return f"[{error_code}] {title} on {service}:\n{guidance}"
    return (
        f"No specific guidance found for error '{error_code}' on {service}. "
        "Recommended next steps: check Azure Service Health, review Application Insights logs, "
        "and consult the official Azure documentation for this service."
    )


# ---------------------------------------------------------------------------
# Agent setup and test runner
# ---------------------------------------------------------------------------


async def main():
    """Create and run OpsAgent for one user query."""

    print("🤖 OpsAgent is ready for one question.\n")

    async_openai = AsyncOpenAI(
        api_key=GITHUB_TOKEN,
        base_url=github_base_url,
    )

    client = OpenAIChatCompletionClient(
        model=GITHUB_MODEL,
        async_client=async_openai,
    )

    agent = Agent(
        client=client,
        name="OpsAgent",
        description="OpsAgent is an AI-powered operations and engineering assistant.",
        instructions="""
        You are OpsAgent, an AI-powered operations and engineering assistant.
        Help developers and cloud engineers troubleshoot issues,
        retrieve documentation, analyze systems, and automate operational workflows.
        Use the available tools when relevant. Keep responses concise, actionable, and practical.
        """,
        tools=[check_azure_service_health, get_deployment_checklist, diagnose_error],
    )

    try:
        query = input("👤 You: ").strip()
    except (EOFError, KeyboardInterrupt):
        print("\n👋 Goodbye!")
        return

    if not query:
        print("No query provided. Exiting.")
        return

    result = await agent.run(query)
    print(f"\n💬 OpsAgent: {result.text}\n")


if __name__ == "__main__":
    asyncio.run(main())
