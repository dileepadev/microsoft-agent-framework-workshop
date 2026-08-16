"""
OpsAgent's tools.

Three operational capabilities, carried over from the previous edition of the
workshop: check a service, get a deployment checklist, diagnose an error code.

Tools are the clearest demonstration of the thesis. Nothing below mentions a
model or a vendor, so every one of these works unchanged whether the agent is
running on Gemini, Claude, a Foundry deployment or a local Ollama model.

Two of the three return canned data. That is stated in their output rather than
hidden, because an agent that invents an Azure status page is worse than no
agent — and because a room full of participants should be able to tell a wired-up
tool from a real integration at a glance.
"""

from __future__ import annotations

import random
from datetime import UTC, datetime
from typing import Annotated

from pydantic import Field

from agent_framework import tool

# NOTE: approval_mode="never_require" keeps the workshop demo moving. These
# three tools only read, so nothing can go wrong. Real tools that write, deploy
# or delete should use "always_require" and let a human confirm the call.


@tool(approval_mode="never_require")
def check_azure_service_health(
    service: Annotated[
        str,
        Field(description="The Azure service to check, e.g. 'App Service', 'AKS', 'Cosmos DB'."),
    ],
    region: Annotated[
        str,
        Field(description="Azure region, e.g. 'East US', 'West Europe'."),
    ] = "East US",
) -> str:
    """Check the current health status of an Azure service in a given region."""
    status = random.choices(
        ["Healthy", "Degraded", "Under investigation"],
        weights=[0.8, 0.15, 0.05],
    )[0]
    checked = datetime.now(UTC).strftime("%Y-%m-%d %H:%M UTC")
    return (
        f"[simulated] Azure {service} in {region}: {status}. Last checked: {checked}. "
        f"This is workshop sample data, not the live Azure Service Health API."
    )


@tool(approval_mode="never_require")
def get_deployment_checklist(
    service_type: Annotated[
        str,
        Field(
            description=(
                "Azure service type, e.g. 'Container App', 'AKS', 'App Service', 'Function App'."
            )
        ),
    ],
) -> str:
    """Return a deployment readiness checklist for the given Azure service type."""
    checklists: dict[str, list[str]] = {
        "container app": [
            "Confirm the container image is pushed to ACR",
            "Set AZURE_RESOURCE_GROUP and AZURE_LOCATION",
            "Run: az containerapp up --name <app> --image <registry>/<image>:<tag>",
            "Configure ingress (external/internal) and the target port",
            "Check replica count and autoscaling rules",
        ],
        "aks": [
            "Configure kubectl: az aks get-credentials --resource-group <rg> --name <cluster>",
            "Validate manifests: kubectl apply --dry-run=client -f <file>",
            "Check node pool capacity and resource quotas",
            "Confirm image pull secrets for the private registry",
            "Apply RBAC and network policies before deploying",
        ],
        "app service": [
            "Verify the App Service plan tier meets the workload",
            "Set app settings: az webapp config appsettings set",
            "Enable a deployment slot for a zero-downtime swap",
            "Configure the health check endpoint under Settings > Health check",
            "Deploy with az webapp deploy or a GitHub Actions workflow",
        ],
        "function app": [
            "Set the storage account connection string (AzureWebJobsStorage)",
            "Choose a Consumption, Premium or Dedicated hosting plan",
            "Set FUNCTIONS_WORKER_RUNTIME to match your language runtime",
            "Deploy with: func azure functionapp publish <app-name>",
            "Enable Application Insights for monitoring and alerting",
        ],
    }

    key = service_type.lower()
    for name, items in checklists.items():
        if name in key:
            steps = "\n".join(f"  - {item}" for item in items)
            return f"Deployment checklist for {service_type}:\n{steps}"

    return (
        f"No specific checklist for {service_type}. General steps:\n"
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
            description=(
                "HTTP status or Azure error code, e.g. '429', '503', 'ResourceNotFound'."
            )
        ),
    ],
    service: Annotated[
        str,
        Field(description="The Azure service or component where the error occurred."),
    ] = "unknown",
) -> str:
    """Diagnose a common error code and return actionable troubleshooting steps."""
    diagnoses: dict[str, tuple[str, list[str]]] = {
        "429": (
            "Too Many Requests / Throttling",
            [
                "Implement exponential backoff with jitter in your retry logic.",
                "Check the Retry-After response header for the required wait.",
                "Review your service tier and consider a quota increase.",
                "For Cosmos DB: monitor RU consumption and scale provisioned throughput.",
            ],
        ),
        "503": (
            "Service Unavailable",
            [
                "The service may be temporarily overloaded or under maintenance.",
                "Check the Azure Service Health dashboard for active incidents.",
                "Verify health check probes are not timing out prematurely.",
                "Retry with exponential backoff; fail over to a second region if configured.",
            ],
        ),
        "resourcenotfound": (
            "Resource Not Found",
            [
                "Confirm the resource name, resource group and subscription ID.",
                "Ensure the resource has not been deleted or moved.",
                "Check RBAC — you may lack read access to the resource.",
                "Verify the request targets the correct Azure region.",
            ],
        ),
        "403": (
            "Forbidden / Authorization Failure",
            [
                "Verify the managed identity or service principal holds the required RBAC roles.",
                "Check for a resource policy or deny assignment blocking the operation.",
                "Ensure the request carries a valid, unexpired bearer token.",
            ],
        ),
        "timeout": (
            "Request Timeout",
            [
                "Increase the client-side timeout in your SDK or HTTP client.",
                "Check the network path: VNet peering, NSG rules and private endpoints.",
                "Review CPU and memory pressure on the target service.",
            ],
        ),
    }

    key = error_code.lower().replace(" ", "")
    for code, (title, steps) in diagnoses.items():
        if code in key:
            guidance = "\n".join(f"  {i}. {step}" for i, step in enumerate(steps, start=1))
            return f"[{error_code}] {title} on {service}:\n{guidance}"

    return (
        f"No specific guidance for error {error_code!r} on {service}. "
        "Next steps: check Azure Service Health, review Application Insights logs, "
        "and consult the Azure documentation for this service."
    )


#: The tools OpsAgent is built with. `agent.py` imports this rather than the
#: individual functions, so adding a tool is a one-line change in one place.
OPSAGENT_TOOLS = [
    check_azure_service_health,
    get_deployment_checklist,
    diagnose_error,
]
