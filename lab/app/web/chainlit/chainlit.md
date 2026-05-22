# OpsAgent

OpsAgent is the workshop's Azure operations assistant, delivered through a branded Chainlit UI.

## Capabilities

- **Tools**: Check Azure service health, build deployment checklists, and diagnose common errors.
- **MCP**: Search Microsoft Learn for official Azure guidance and troubleshooting steps.
- **Workflow**: Run `/workflow <query>` for severity tagging and guided triage.
- **Memory**: Keep context across turns and remember details you share during the session.

## Example Prompts

- `Check Azure App Service health in East US`
- `Give me a deployment checklist for Azure Functions`
- `Use Microsoft Learn to explain how to restart an Azure App Service`
- `/workflow production API latency spiked after deployment`
- `My name is Alex` then `What is my name?`

## What You Will See

- Live streamed responses as OpsAgent works
- `Tool: ...` steps when a built-in operation runs
- `MCP: ...` steps when Microsoft Learn is queried
- Workflow results inside the chat thread

Start a chat to explore tools, MCP lookups, and workflow triage in one place.
