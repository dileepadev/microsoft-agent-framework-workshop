# 9. Chat User Interface

Bring all previous modules together in four fully working interfaces: an
interactive CLI, two web UIs (Chainlit and Streamlit), and a FastAPI REST API
with a demo client — each powered by the same OpsAgent.

## Module Goals

| Goal | Covered by |
| --- | --- |
| Build a runnable CLI chat for rapid local testing | `lab/app/cli/main.py` |
| Create a polished web chat with built-in UI | `lab/app/web/chainlit/app.py` |
| Create a customisable web chat with Streamlit | `lab/app/web/streamlit/app.py` |
| Expose OpsAgent as a REST API | `lab/app/web/fastapi/server.py` |
| Consume the API from a Python client | `lab/app/web/fastapi/client.py` |
| Reuse every prior module in all interfaces | Shared `app/shared/` layer |

## In This Module

Every interface activates the same full feature set:

| Module | Feature |
| --- | --- |
| Module 4 | **Tools** — Azure health check, deployment checklist, error diagnosis |
| Module 5 | **MCP** — Microsoft Learn documentation lookup |
| Module 6 | **Multi-Turn** — persistent conversation history per session |
| Module 7 | **Memory** — `UserMemoryProvider` remembers the user's name |
| Module 8 | **Workflow** — three-step triage pipeline (severity tag → agent → output) |

A shared module layer (`app/shared/`) contains the agent factory, workflow
builder, tools, memory provider, and supporting MCP helpers so each interface
imports them without duplication.

## Folder Structure

```text
lab/
└── app/
    ├── shared/
    │   ├── agent.py        # Agent factory, workflow builder, classify_severity
    │   ├── mcp.py          # Microsoft Learn / MCP integration helpers
    │   ├── providers.py    # Module 7 UserMemoryProvider
    │   ├── tools.py        # Module 4 tools (re-exported)
    │   └── workflow.py     # Module 8 triage workflow builder
    ├── cli/
    │   ├── main.py         # Interactive CLI
    │   └── README.md
    └── web/
        ├── chainlit/
        │   ├── app.py      # Chainlit web chat
        │   ├── launcher.py # Chainlit app launcher
        │   ├── chainlit.md
        │   └── README.md
        ├── streamlit/
        │   ├── app.py      # Streamlit web chat
        │   └── README.md
        └── fastapi/
            ├── server.py   # FastAPI REST API
            ├── client.py   # Demo HTTP client
            └── README.md
```

## Prerequisites

- Completed Modules 1 – 8.
- The `lab/.env` file contains `GITHUB_TOKEN` and `GITHUB_MODEL`.
- The `lab` virtual environment is active (`.venv`).

## Step 1 — Verify Dependencies

`fastapi` and `uvicorn` were added in this module. Confirm they are installed:

```bash
cd lab
uv sync
```

If you need to add them manually:

```bash
uv add "fastapi[standard]"
```

## Step 2 — Explore the Shared Layer

Open `lab/app/shared/agent.py`. It provides three public functions used by all
four interfaces:

| Function | What it does |
| --- | --- |
| `create_chat_client(token, model)` | Returns a configured `OpenAIChatCompletionClient` |
| `create_ops_agent(client)` | Returns an `Agent` wired with all Module 4–7 features |
| `build_triage_workflow(client)` | Returns a compiled Module 8 `Workflow` |

`classify_severity(query)` is also exported for interfaces that want to show
the severity label before running the workflow.

## Step 3 — Run the CLI

The CLI is the fastest way to test OpsAgent interactively.

```bash
cd lab/app/cli
python main.py
```

**Available commands inside the CLI:**

| Input | Effect |
| --- | --- |
| Any text | Regular multi-turn chat (Modules 4 – 7 active) |
| `!workflow <query>` | Runs the Module 8 triage pipeline |
| `!state` | Prints current session state (user name from Module 7) |
| `!help` | Lists all commands |
| `exit` or `quit` | Exits the CLI |

**Expected output (first turn):**

```text
╔══════════════════════════════════════════════════════════╗
║          OpsAgent CLI — Module 9                         ║
║  Active features:                                        ║
║    ✅ Module 4 — Tools                                   ║
║    ✅ Module 5 — MCP (Microsoft Learn)                   ║
║    ✅ Module 6 — Multi-Turn History                      ║
║    ✅ Module 7 — User Memory                             ║
║    ✅ Module 8 — Workflow  (!workflow <query>)            ║
╚══════════════════════════════════════════════════════════╝
👤 You:
```

## Step 4 — Run the Chainlit Web Chat

Chainlit provides a ready-made chat UI with no custom HTML required.

```bash
cd lab
python -m app.web.chainlit.launcher
```

Open <http://localhost:8000> in your browser.

The launcher sets `CHAINLIT_APP_ROOT` to `lab/app/web/chainlit`, so Chainlit stores its `.chainlit/` and `.files/` folders next to the Chainlit app instead of under `lab/`.

**Workflow command:** in the chat input, type:

```text
/workflow production database is down
```

This triggers the Module 8 triage pipeline and returns OpsAgent's
resolution steps inside the chat thread.

**How the lifecycle works:**

| Event | Action |
| --- | --- |
| `on_chat_start` | Creates `OpenAIChatCompletionClient`, calls `agent.__aenter__()`, creates session |
| `on_message` | Dispatches to `/workflow` handler or regular `agent.run()` |
| `on_chat_end` | Calls `agent.__aexit__()` to release MCP connections |

## Step 5 — Run the Streamlit Web Chat

```bash
cd lab/app/web/streamlit
streamlit run app.py
```

Open <http://localhost:8501> in your browser.

**Sidebar features:**

- Active module list
- **Run Triage Workflow** panel — enter a query and click **▶ Run Workflow**
- **Session State** viewer — shows the user name captured by Module 7
- **Clear Chat** button

**Why a background thread?**  Streamlit re-runs the entire script on every
user interaction. The `SyncOpsAgent` class keeps a dedicated `asyncio` event
loop alive in a daemon thread so the async agent, its MCP connections, and its
session state all persist across re-runs.

## Step 6 — Run the FastAPI API and Client

### Start the server

```bash
cd lab/app/web/fastapi
fastapi dev server.py
```

Open <http://localhost:8000/docs> for the interactive Swagger UI.

### Endpoints

| Method | Path | Description |
| --- | --- | --- |
| `GET` | `/api/health` | Health check |
| `POST` | `/api/chat` | Multi-turn chat |
| `POST` | `/api/workflow` | Run the triage pipeline |

### Multi-turn chat request

```json
POST /api/chat
{
  "message": "My name is Alex. What can you help me with?",
  "session_id": "my-session"
}
```

Pass the same `session_id` on every request to preserve conversation history
(Module 6) and user memory (Module 7).

### Workflow request

```json
POST /api/workflow
{
  "query": "production server is down!"
}
```

Response:

```json
{
  "severity": "CRITICAL",
  "query": "production server is down!",
  "response": "1. Verify network connectivity…"
}
```

### Run the demo client

In a separate terminal (server must be running):

```bash
cd lab/app/web/fastapi
python client.py
```

The client demonstrates a three-turn chat (name introduction → tool call →
name recall) and three workflow queries using the same `session_id`.

## Expected Outcomes

After completing this module you will have:

- ✅ An interactive CLI that exercises every workshop module
- ✅ A Chainlit web chat with `/workflow` command support
- ✅ A Streamlit web chat with a sidebar workflow panel and session state viewer
- ✅ A FastAPI server exposing OpsAgent as a REST API
- ✅ A demo HTTP client validating multi-turn memory and workflow across API calls
- ✅ A shared `app/shared/` layer that prevents code duplication

## Key Concepts

| Concept | Where it appears |
| --- | --- |
| Shared agent factory | `app/shared/agent.py` — `create_ops_agent()` |
| Async lifecycle management | CLI: `async with agent`; Chainlit: `__aenter__`/`__aexit__`; FastAPI: `lifespan` context |
| Async-to-sync bridge | Streamlit `SyncOpsAgent` — background thread + `asyncio.run_coroutine_threadsafe` |
| Per-session history | `InMemoryHistoryProvider(load_messages=True)` inside the agent |
| User memory | `UserMemoryProvider` — extracts and injects user name across turns |
| Triage workflow | `build_triage_workflow()` — `triage_input → agent → capture_output` |
| Session isolation | FastAPI `_sessions` dict; Streamlit `st.session_state`; Chainlit `cl.user_session` |

## Next

Continue to [10. Host Agent](./10-host-agent.md).
