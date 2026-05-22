# 10. Host Agent

Host OpsAgent so users and other agents can reach it over HTTP — deploying the
same agent built through Modules 4–9 into a production-ready serverless endpoint
using the Azure Functions (Durable) hosting option.

## Module Goals

| Goal | Covered by |
| --- | --- |
| Understand the four hosting options | Hosting Options table |
| Install the Azure Functions hosting package | Step 1 |
| Start the Azurite local storage emulator | Step 2 |
| Configure `local.settings.json` | Step 3 |
| Run the Functions host | Step 4 |
| Invoke the hosted endpoint with `curl` | Step 5 |

## In This Module

Once an agent works in a REPL or chat UI, the next step is to make it available
over HTTP so other systems, agents, or clients can call it. Microsoft Agent
Framework provides four hosting options:

| Option | Description | Best For |
| --- | --- | --- |
| **A2A Protocol** | Expose agents via the Agent-to-Agent protocol | Multi-agent systems |
| **OpenAI-Compatible Endpoints** | Expose agents via Chat Completions or Responses APIs | OpenAI-compatible clients |
| **Azure Functions (Durable)** | Run agents as durable Azure Functions | Serverless, long-running tasks |
| **AG-UI Protocol** | Build web-based AI agent applications | Web frontends |

This module uses **Azure Functions (Durable)** because it is the most portable
serverless option: OpsAgent and its full feature set (Tools, MCP, Multi-Turn)
run inside a standard HTTP-triggered function with durable state management that
survives restarts and scales to zero when idle.

> Source: [Microsoft Learn — Host Your Agent](https://learn.microsoft.com/agent-framework/get-started/hosting)

## Folder Structure

```text
lab/
└── app/
    └── hosting/
        ├── function_app.py                  # OpsAgent + AgentFunctionApp
        ├── host.json                        # Azure Functions host config
        ├── local.settings.json.template     # Settings template (git tracked)
        ├── local.settings.json              # Actual settings (gitignored)
        ├── requirements.txt                 # Python deps for Azure deployment
        └── README.md
```

## Prerequisites

- Completed Modules 1 – 9.
- The `lab/.env` file contains `GITHUB_TOKEN` and `GITHUB_MODEL`.
- The `lab` virtual environment is active (`.venv`).
- [Azure Functions Core Tools 4.x](https://learn.microsoft.com/en-us/azure/azure-functions/functions-run-local) installed (`func` on `PATH`).
- [Azurite](https://learn.microsoft.com/en-us/azure/storage/common/storage-use-azurite) — local Azure Storage emulator for durable state.

## Step 1 — Install the Azure Functions Hosting Package

The `agent-framework-azurefunctions` package adds `AgentFunctionApp` and all
durable task infrastructure needed to host agents.

```bash
cd lab
uv add agent-framework-azurefunctions --prerelease=allow
```

> [!NOTE]
> This is a pre-release add-on to `agent-framework`, separate from the core
> package already in `pyproject.toml`.

## Step 2 — Start Azurite

The durable extension uses Azure Storage for state persistence. Azurite emulates
this locally so no real Azure subscription is needed.

```bash
# Install once
npm install -g azurite

# Start (leave this terminal open)
azurite --silent --location /tmp/azurite
```

Azurite listens on `http://localhost:10000` (Blob), `10001` (Queue), and
`10002` (Table). The `local.settings.json` uses
`"AzureWebJobsStorage": "UseDevelopmentStorage=true"` to connect to it automatically.

## Step 3 — Configure `local.settings.json`

Inside `lab/app/hosting/`, copy the template and fill in your credentials:

```bash
cd lab/app/hosting
cp local.settings.json.template local.settings.json
```

Edit `local.settings.json` and replace `<your-github-pat>` with your token.
This file is gitignored so secrets stay local.

**`local.settings.json` reference:**

```json
{
  "IsEncrypted": false,
  "Values": {
    "FUNCTIONS_WORKER_RUNTIME": "python",
    "AzureWebJobsStorage": "UseDevelopmentStorage=true",
    "DURABLE_TASK_SCHEDULER_CONNECTION_STRING": "Endpoint=http://localhost:8080;TaskHub=default;Authentication=None",
    "TASKHUB_NAME": "default",
    "GITHUB_TOKEN": "<your-github-pat>",
    "GITHUB_MODEL": "gpt-4o-mini"
  }
}
```

## Step 4 — Start the Functions Host

Open a new terminal (Azurite must still be running):

```bash
cd lab/app/hosting
func start
```

You will see:

```text
Functions:

    health_check: [GET] http://localhost:7071/api/health

    http-OpsAgent: [POST] http://localhost:7071/api/agents/OpsAgent/run

    dafx-OpsAgent: entityTrigger
```

## Step 5 — Invoke the Hosted Endpoint

### Single turn

```bash
curl -i -X POST http://localhost:7071/api/agents/OpsAgent/run \
  -H "Content-Type: text/plain" \
  -d "Check the health of App Service in East US."
```

Expected response:

```text
HTTP/1.1 200 OK
Content-Type: text/plain; charset=utf-8
x-ms-thread-id: <guid>

Azure App Service in East US: Healthy. Last checked: 2026-05-22 10:00 UTC
```

### Multi-turn conversation

Pass the `x-ms-thread-id` from the first response as `?thread_id=` to continue
the same conversation:

```bash
# First turn
curl -i -X POST http://localhost:7071/api/agents/OpsAgent/run \
  -H "Content-Type: text/plain" \
  -d "My name is Alex. What can you help me with?"

# Second turn — replace <id> with the x-ms-thread-id value
curl -X POST "http://localhost:7071/api/agents/OpsAgent/run?thread_id=<id>" \
  -H "Content-Type: text/plain" \
  -d "What tools do you have available?"
```

### Async mode (HTTP 202 — fire and forget)

```bash
curl -i -X POST http://localhost:7071/api/agents/OpsAgent/run \
  -H "Content-Type: text/plain" \
  -H "x-ms-wait-for-response: false" \
  -d "Get the AKS deployment checklist."
```

## Expected Outcomes

After completing this module you will have:

- ✅ A self-contained hosting example under `lab/app/hosting/`
- ✅ A locally running HTTP endpoint at `POST /api/agents/OpsAgent/run`
- ✅ Multi-turn conversation state preserved via `x-ms-thread-id`
- ✅ All Module 4–6 features active in the hosted endpoint

## Key Concepts

| Concept | Where it appears |
| --- | --- |
| `AgentFunctionApp` | `function_app.py` — wraps the agent and registers HTTP endpoints |
| Durable state | Conversation threads persist across invocations via the Durable Task Scheduler |
| `x-ms-thread-id` | Returned on first call; pass as `?thread_id=` to continue a conversation |
| Azurite | Local Azure Storage emulator — required for durable state in local development |
| A2A Protocol | Alternative for multi-agent systems — [learn more](https://learn.microsoft.com/agent-framework/integrations/a2a) |
| OpenAI-Compatible Endpoints | Alternative for OpenAI-compatible clients — [learn more](https://learn.microsoft.com/agent-framework/integrations/openai-endpoints) |
| AG-UI Protocol | Alternative for web frontends — [learn more](https://learn.microsoft.com/agent-framework/integrations/ag-ui/) |

## Reference

- [Microsoft Learn — Host Your Agent](https://learn.microsoft.com/agent-framework/get-started/hosting)
- [Azure Functions Durable Extension](https://learn.microsoft.com/agent-framework/integrations/azure-functions)
