# OpsAgent — Streamlit

Web chat interface powered by Streamlit — Module 9.

## Run

```bash
# From lab/app/web/streamlit/:
streamlit run app.py
```

Open <http://localhost:8501> in your browser.

## Features

| Module | Feature |
| --- | --- |
| Module 4 | Tools — Azure health check, deployment checklist, error diagnosis |
| Module 5 | MCP — Microsoft Learn documentation |
| Module 6 | Multi-turn — session persists across all messages in the tab |
| Module 7 | Memory — OpsAgent remembers your name |
| Module 8 | Workflow — sidebar **Run Triage Workflow** panel |

## Triage Workflow

In the sidebar, enter an ops query (e.g. `production server is down`) and click
**▶ Run Workflow** to trigger the Module 8 triage pipeline.

## How async is handled

Streamlit is synchronous. The `SyncOpsAgent` class keeps a dedicated asyncio
event loop alive in a background thread so the async agent can run multiple
turns with full session and memory support.
