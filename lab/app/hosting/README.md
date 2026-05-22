# OpsAgent — Azure Functions Hosting

This sample shows how to host OpsAgent as a durable Azure Function using the
[Agent Framework Azure Functions extension](https://learn.microsoft.com/agent-framework/integrations/azure-functions).

The same OpsAgent you built through Modules 4–9 is exposed as a stateful HTTP
endpoint at `POST /api/agents/OpsAgent/run`.

## Key Concepts

| Concept | Detail |
| --- | --- |
| `AgentFunctionApp` | Wraps the agent and registers HTTP triggers automatically |
| Durable state | Conversation threads persist across requests via Azure Storage |
| `x-ms-thread-id` header | Returned on first call; pass as `?thread_id=` to continue a conversation |
| Multi-turn history | `InMemoryHistoryProvider` keeps context within a thread |

## Prerequisites

- [Azure Functions Core Tools 4.x](https://learn.microsoft.com/en-us/azure/azure-functions/functions-run-local) (`func` on PATH)
- [Azurite](https://learn.microsoft.com/en-us/azure/storage/common/storage-use-azurite) — local Azure Storage emulator
- `agent-framework-azurefunctions` installed in the active virtual environment
- `GITHUB_TOKEN` and `GITHUB_MODEL` available (via `local.settings.json` or `.env`)

## Setup

### 1. Install the hosting package

From the `lab/` folder:

```bash
uv add agent-framework-azurefunctions --prerelease=allow
```

### 2. Configure `local.settings.json`

Copy the template and fill in your GitHub credentials:

```bash
cp local.settings.json.template local.settings.json
```

Edit `local.settings.json` and replace `<your-github-pat>` with your token.

### 3. Start Azurite

Azurite provides local Azure Storage for durable state management.

```bash
# Using npm (recommended)
npx azurite --silent --location /tmp/azurite --debug /tmp/azurite/debug.log
```

Or install once and run:

```bash
npm install -g azurite
azurite --silent --location /tmp/azurite
```

### 4. Start the Functions host

Open a new terminal:

```bash
cd lab/app/hosting
func start
```

You should see:

```text
Functions:

    OpsAgent: [POST] http://localhost:7071/api/agents/OpsAgent/run
```

## Invoke OpsAgent

### Single turn

```bash
curl -i -X POST http://localhost:7071/api/agents/OpsAgent/run \
     -H "Content-Type: text/plain" \
     -d "Check the health of App Service in East US."
```

Response:

```text
HTTP/1.1 200 OK
Content-Type: text/plain; charset=utf-8
x-ms-thread-id: <guid>

Azure App Service in East US: Healthy. Last checked: 2026-05-22 10:00 UTC
```

### Multi-turn (pass `x-ms-thread-id` as `?thread_id=`)

```bash
# First turn — save the thread ID from the response header
THREAD_ID=$(curl -si -X POST http://localhost:7071/api/agents/OpsAgent/run \
     -H "Content-Type: text/plain" \
     -d "My name is Alex. What can you help me with?" \
     | grep -i x-ms-thread-id | awk '{print $2}' | tr -d '\r')

# Second turn — continue the same conversation
curl -X POST "http://localhost:7071/api/agents/OpsAgent/run?thread_id=$THREAD_ID" \
     -H "Content-Type: text/plain" \
     -d "What tools do you have available?"
```

### Async mode (returns HTTP 202 immediately)

```bash
curl -i -X POST http://localhost:7071/api/agents/OpsAgent/run \
     -H "Content-Type: text/plain" \
     -H "x-ms-wait-for-response: false" \
     -d "Check the AKS deployment checklist."
```

## File Structure

```text
lab/app/hosting/
├── function_app.py                  # OpsAgent + AgentFunctionApp registration
├── host.json                        # Azure Functions host config (durable task)
├── local.settings.json.template     # Settings template (git tracked)
├── local.settings.json              # Actual settings with credentials (gitignored)
├── requirements.txt                 # Python dependencies for Azure deployment
└── README.md
```

## Reference

- [Microsoft Learn — Host Your Agent](https://learn.microsoft.com/agent-framework/get-started/hosting)
- [Azure Functions Durable Extension for Agent Framework](https://learn.microsoft.com/agent-framework/integrations/azure-functions)
- [Official samples — azure_functions/01_single_agent](https://github.com/microsoft/agent-framework/tree/main/python/samples/04-hosting/azure_functions/01_single_agent)
