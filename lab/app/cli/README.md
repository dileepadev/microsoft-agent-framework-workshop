# OpsAgent CLI

Interactive command-line chat interface — Module 9.

Combines Module 4 (tools), Module 5 (MCP), Module 6 (multi-turn),
Module 7 (memory), and Module 8 (workflow) into one session.

## Run

```bash
# From the lab/ folder:
python app/cli/main.py

# Or with uv:
uv run app/cli/main.py
```

## Commands

| Command | Description |
| --- | --- |
| `!help` | Show available commands |
| `!state` | Show session state (stored user name) |
| `!workflow <query>` | Run the triage pipeline on a query |
| `exit` / `quit` | Exit |

## Example session

```text
👤 You: My name is Alex. What can you help me with?
💬 OpsAgent: Hi Alex! I can help you with Azure health checks...

👤 You: Check App Service health in West Europe
💬 OpsAgent: Azure App Service in West Europe: Healthy. Last checked: ...

👤 You: !workflow production database is down
  🔍 Triage:  [CRITICAL] production database is down
  💬 OpsAgent (Workflow): 1. Verify connectivity... 2. Check logs...

👤 You: !state
📦 Session State → user_name: Alex
```
