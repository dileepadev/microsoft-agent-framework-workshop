# Microsoft Agent Framework Workshop

Build production-ready AI agents from scratch using **Microsoft Agent Framework**, **GitHub Models**, and **MCP servers** — a hands-on, module-by-module workshop.

[Start Workshop](getting-started/1-environment-setup) | [Explore OpsAgent](opsagent)

---

## What You Will Build

Throughout this workshop you will build **OpsAgent** — an AI-powered operations and engineering assistant that helps developers and cloud engineers troubleshoot issues, retrieve documentation, and automate workflows.

By the end, OpsAgent will be a fully hosted HTTP endpoint with:

<div class="grid cards" markdown>

- :material-tools: **Tool Calling** — Custom Python functions as agent tools
- :material-connection: **MCP Integration** — Microsoft Learn live documentation via MCP
- :material-history: **Multi-Turn Memory** — Persistent conversation history across sessions
- :material-sitemap: **Workflows** — Orchestrated multi-agent pipelines
- :material-chat: **Chat UI** — Streamlit, Chainlit, and FastAPI frontends
- :material-cloud-upload: **Hosted Endpoint** — Azure Functions (Durable) deployment

</div>

---

## Workshop Modules

| # | Module | What You Build |
|---|--------|---------------|
| 1 | [Environment Setup](getting-started/1-environment-setup) | Python project, venv, dependencies |
| 2 | [GitHub Models Connection](getting-started/2-github-models-connection) | LLM client via GitHub Models |
| 3 | [Agent Framework Agents](getting-started/3-microsoft-agent-framework-agents) | First OpsAgent with instructions |
| 4 | [Tool Calling](getting-started/4-tool-calling) | Azure health check & deployment tools |
| 5 | [MCP Integration](getting-started/5-mcp-integration) | Microsoft Learn MCP server |
| 6 | [Multi-Turn Conversations](getting-started/6-multi-turn-conversations) | Conversation history & memory |
| 7 | [Memory & Persistence](getting-started/7-memory-and-persistence) | Persistent agent memory |
| 8 | [Workflows](getting-started/8-workflows) | Multi-agent orchestration |
| 9 | [Chat User Interface](getting-started/9-chat-user-interface) | Streamlit, Chainlit, FastAPI UIs |
| 10 | [Host Agent](getting-started/10-host-agent) | Azure Functions HTTP endpoint |

---

## Tech Stack

- **Python 3.10+** — Agent logic and tooling
- **Microsoft Agent Framework** — Core agent SDK
- **GitHub Models** — Free LLM inference (GPT-4o mini)
- **MCP (Model Context Protocol)** — Live documentation retrieval
- **Azure Functions** — Serverless hosting
- **Streamlit / Chainlit / FastAPI** — Chat interfaces
