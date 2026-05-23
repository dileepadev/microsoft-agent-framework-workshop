# Microsoft Agent Framework Workshop

A hands-on workshop for building OpsAgent, an AI-powered operations assistant, with Microsoft Agent Framework, GitHub Models, MCP, multi-turn memory, workflows, and multiple chat interfaces.

- Live workshop site: <https://dileepadev.github.io/microsoft-agent-framework-workshop/>
- Workshop docs source: [docs/](docs/)
- Runnable lab project: [lab/](lab/)

## What You Build

Across 10 modules, this repo walks you from a basic agent to a hosted OpsAgent with:

- GitHub Models-backed chat completions
- Tool calling for Azure-oriented operational tasks
- Microsoft Learn access through MCP
- Multi-turn conversations and session memory
- A triage workflow pipeline
- Multiple user interfaces:
  - CLI
  - Chainlit
  - Streamlit
  - FastAPI
- Azure Functions hosting

## Repository Overview

This repository has two main parts:

1. The Astro documentation site at the repo root.
2. The Python workshop lab in [lab/](lab/) where the agent code, demos, and module-by-module scripts live.

The root site is built with Astro and deployed to GitHub Pages. The lab is a separate Python project managed with `uv` and locked by [lab/uv.lock](lab/uv.lock).

## Workshop Modules

| Module | Topic | Main guide |
| --- | --- | --- |
| 1 | Environment Setup | [docs/getting-started/1-environment-setup.md](docs/getting-started/1-environment-setup.md) |
| 2 | GitHub Models Connection | [docs/getting-started/2-github-models-connection.md](docs/getting-started/2-github-models-connection.md) |
| 3 | Microsoft Agent Framework Agents | [docs/getting-started/3-microsoft-agent-framework-agents.md](docs/getting-started/3-microsoft-agent-framework-agents.md) |
| 4 | Tool Calling | [docs/getting-started/4-tool-calling.md](docs/getting-started/4-tool-calling.md) |
| 5 | MCP Integration | [docs/getting-started/5-mcp-integration.md](docs/getting-started/5-mcp-integration.md) |
| 6 | Multi-Turn Conversations | [docs/getting-started/6-multi-turn-conversations.md](docs/getting-started/6-multi-turn-conversations.md) |
| 7 | Memory and Persistence | [docs/getting-started/7-memory-and-persistence.md](docs/getting-started/7-memory-and-persistence.md) |
| 8 | Workflows | [docs/getting-started/8-workflows.md](docs/getting-started/8-workflows.md) |
| 9 | Chat User Interface | [docs/getting-started/9-chat-user-interface.md](docs/getting-started/9-chat-user-interface.md) |
| 10 | Host Agent | [docs/getting-started/10-host-agent.md](docs/getting-started/10-host-agent.md) |

## Prerequisites

Before starting, make sure you have:

- Python 3.12+
- `uv`
- Node.js and `npm` for the Astro docs site
- A GitHub account and a token for GitHub Models
- Basic Python knowledge

Optional for Module 10:

- Azure Functions Core Tools 4.x
- Azurite

## Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/dileepadev/microsoft-agent-framework-workshop.git
cd microsoft-agent-framework-workshop
```

### 2. Run the documentation site

Install the root site dependencies and start Astro locally:

```bash
npm install
npm run dev
```

Use `npm run build` to generate the static site into `dist/`.

### 3. Set up the Python lab

The runnable workshop code lives in [lab/](lab/).

```bash
cd lab
uv sync
cp .env.example .env
```

Activate the virtual environment:

```bash
# macOS / Linux
source .venv/bin/activate

# Windows
.venv\Scripts\activate
```

Then edit `.env` and set:

```env
GITHUB_TOKEN=your_github_token
GITHUB_MODEL=gpt-4o-mini
```

You can create a token at <https://github.com/settings/tokens>.

## Running the Lab Applications

All commands below assume you are starting from the repo root unless noted otherwise.

### CLI

```bash
cd lab
uv run app/cli/main.py
```

Available commands in the CLI:

- `!help`
- `!state`
- `!workflow <query>`
- `exit` / `quit`

### Chainlit

```bash
cd lab
python -m app.web.chainlit.launcher -w
```

Open <http://localhost:8000>.

### Streamlit

```bash
cd lab/app/web/streamlit
streamlit run app.py
```

Open <http://localhost:8501>.

### FastAPI

Start the API server:

```bash
cd lab/app/web/fastapi
uvicorn server:app --reload
```

Open <http://localhost:8000/docs>.

Run the demo client in a separate terminal:

```bash
cd lab/app/web/fastapi
python client.py
```

### Azure Functions hosting

The hosting sample is in [lab/app/hosting/](lab/app/hosting/). See:

- [docs/getting-started/10-host-agent.md](docs/getting-started/10-host-agent.md)
- [lab/app/hosting/README.md](lab/app/hosting/README.md)

## Module Smoke Tests and Demos

The lab includes runnable scripts for each core module:

```bash
cd lab
uv run test_github_models_connection.py
uv run test_microsoft_agent_framework.py
uv run test_tool_calling.py
uv run test_mcp_integration.py
uv run test_multi_turn_conversations.py
uv run test_memory_persistence.py
uv run test_workflows.py
```

These are interactive demo scripts rather than a conventional automated test suite.

## Current Project Structure

```text
.
├── docs/                        # Workshop content in Markdown
├── public/                      # Static assets for the Astro site
├── src/                         # Astro pages, layouts, components, styles
├── lab/
│   ├── .env.example             # Environment variable template
│   ├── app/
│   │   ├── shared/              # Agent factory, tools, MCP, memory, workflow
│   │   ├── cli/                 # CLI interface
│   │   ├── hosting/             # Azure Functions hosting sample
│   │   └── web/
│   │       ├── chainlit/        # Chainlit UI
│   │       ├── fastapi/         # FastAPI server and demo client
│   │       └── streamlit/       # Streamlit UI
│   ├── pyproject.toml           # Python project configuration
│   ├── requirements.txt         # Simple dependency list
│   ├── uv.lock                  # Locked Python dependencies
│   └── test_*.py                # Module-by-module demo scripts
├── astro.config.mjs             # Astro site configuration
├── package.json                 # Astro scripts and dependencies
└── README.md
```

## Tech Stack

- Microsoft Agent Framework
- GitHub Models
- MCP (Model Context Protocol)
- Chainlit
- Streamlit
- FastAPI
- Azure Functions
- Astro
- Tailwind CSS
- `uv`

## Resources

- Microsoft Agent Framework: <https://learn.microsoft.com/agent-framework/>
- GitHub Models: <https://docs.github.com/en/github-models>
- Model Context Protocol: <https://modelcontextprotocol.io/introduction>
- Chainlit: <https://docs.chainlit.io/>
- Streamlit: <https://docs.streamlit.io/>
- FastAPI: <https://fastapi.tiangolo.com/>
- Astro: <https://docs.astro.build/>
- uv: <https://docs.astral.sh/uv/>

## License

MIT License. See [LICENSE](LICENSE).

## Contributing

Issues and pull requests are welcome.
