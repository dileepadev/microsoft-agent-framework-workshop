# Microsoft Agent Framework Workshop

A hands-on workshop teaching how to build AI chat agents using Microsoft Agent Framework, GitHub Models, MCP, and modern AI application patterns.

- [Microsoft Agent Framework Workshop](#microsoft-agent-framework-workshop)
  - [Introduction](#introduction)
  - [What You'll Build](#what-youll-build)
  - [Prerequisites](#prerequisites)
  - [Tech Stack](#tech-stack)
  - [Getting Started](#getting-started)
    - [Module 1: Environment Setup](#module-1-environment-setup)
    - [Module 2: GitHub Models Connection](#module-2-github-models-connection)
    - [Module 3: Microsoft Agent Framework Agents](#module-3-microsoft-agent-framework-agents)
    - [Module 4: Tool Calling](#module-4-tool-calling)
    - [Module 5: MCP Integration](#module-5-mcp-integration)
    - [Module 6: Multi-Turn Conversations](#module-6-multi-turn-conversations)
    - [Module 7: Memory and Persistence](#module-7-memory-and-persistence)
    - [Module 8: Workflows](#module-8-workflows)
    - [Module 9: Chat User Interface](#module-9-chat-user-interface)
    - [Module 10: Host Agent](#module-10-host-agent)
  - [Quick Setup (Reference)](#quick-setup-reference)
    - [Clone the Repository](#clone-the-repository)
    - [Install uv](#install-uv)
    - [Create Virtual Environment](#create-virtual-environment)
    - [Install Dependencies](#install-dependencies)
    - [Environment Variables](#environment-variables)
  - [Project Structure](#project-structure)
  - [Workshop Topics](#workshop-topics)
  - [Running the Applications](#running-the-applications)
    - [Chainlit App](#chainlit-app)
    - [Streamlit App](#streamlit-app)
    - [Additional UI Variants](#additional-ui-variants)
  - [Recommended VS Code Extensions](#recommended-vs-code-extensions)
  - [Resources](#resources)
  - [License](#license)
  - [Contributing](#contributing)

## Introduction

This workshop walks through the fundamentals of building AI-powered chat agents using the Microsoft Agent Framework.

You'll learn how to:

- Create conversational AI agents
- Integrate GitHub Models
- Add memory and tool calling
- Connect external tools using MCP (Model Context Protocol)
- Build interactive web-based chat interfaces

The workshop is beginner-friendly and focused on practical implementation.

## What You'll Build

By the end of this workshop, you'll build a fully functional AI chat agent with:

- Web-based chat interfaces
  - Chainlit
  - Streamlit
  - Additional UI variants
- Conversation memory
- Tool calling capabilities
- MCP (Model Context Protocol) integration
- GitHub Models integration
- Modular and extensible architecture

## Prerequisites

Before starting, make sure you have:

- Python 3.10+
- uv (Python package & environment manager)
- GitHub account (for GitHub Models access)
- Basic Python knowledge

## Tech Stack

This workshop uses:

- Microsoft Agent Framework
- GitHub Models
- UI frameworks:
  - Chainlit
  - Streamlit
  - Additional variants (TBD)
- MCP (Model Context Protocol)
- uv (Python package & environment manager)

## Getting Started

Follow the workshop in order. Each module has a dedicated guide:

### Module 1: Environment Setup

- Guide: [docs/getting-started/1-environment-setup.md](docs/getting-started/1-environment-setup.md)

### Module 2: GitHub Models Connection

- Guide: [docs/getting-started/2-github-models-connection.md](docs/getting-started/2-github-models-connection.md)

### Module 3: Microsoft Agent Framework Agents

- Guide: [docs/getting-started/3-microsoft-agent-framework-agents.md](docs/getting-started/3-microsoft-agent-framework-agents.md)

### Module 4: Tool Calling

- Guide: [docs/getting-started/4-tool-calling.md](docs/getting-started/4-tool-calling.md)

### Module 5: MCP Integration

- Guide: [docs/getting-started/5-mcp-integration.md](docs/getting-started/5-mcp-integration.md)

### Module 6: Multi-Turn Conversations

- Guide: [docs/getting-started/6-multi-turn-conversations.md](docs/getting-started/6-multi-turn-conversations.md)

### Module 7: Memory and Persistence

- Guide: [docs/getting-started/7-memory-and-persistence.md](docs/getting-started/7-memory-and-persistence.md)

### Module 8: Workflows

- Guide: [docs/getting-started/8-workflows.md](docs/getting-started/8-workflows.md)

### Module 9: Chat User Interface

- Guide: [docs/getting-started/9-chat-user-interface.md](docs/getting-started/9-chat-user-interface.md)

### Module 10: Host Agent

- Guide: [docs/getting-started/10-host-agent.md](docs/getting-started/10-host-agent.md)

## Quick Setup (Reference)

Use this section if you want the core setup commands in one place.

### Clone the Repository

```bash
# Using HTTPS:
git clone https://github.com/dileepadev/microsoft-agent-framework-workshop.git
# Using SSH:
git clone git@github.com:dileepadev/microsoft-agent-framework-workshop.git

# Navigate into the project directory
cd microsoft-agent-framework-workshop
```

### Install uv

```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

```powershell
# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Verify installation:

```bash
uv --version
```

### Create Virtual Environment

```bash
uv venv
```

Activate the environment:

```bash
# macOS / Linux
source .venv/bin/activate
```

```bash
# Windows
.venv\Scripts\activate
```

### Install Dependencies

```bash
uv pip install -r requirements.txt
```

### Environment Variables

Create a `.env` file in the project root:

```env
GITHUB_TOKEN=your_github_token
GITHUB_MODEL=gpt-4o-mini
```

> [!NOTE]
> You can generate a GitHub token from:
> <https://github.com/settings/tokens>

## Project Structure

```text
.
├── apps/
│   ├── chainlit/
│   ├── streamlit/
│   └── other-variants/
├── agents/
├── tools/
├── mcp/
├── notebooks/
├── docs/
│   └── getting-started/
│       ├── 1-environment-setup.md
│       ├── 2-github-models-connection.md
│       ├── 3-microsoft-agent-framework-agents.md
│       ├── 4-tool-calling.md
│       ├── 5-mcp-integration.md
│       ├── 6-multi-turn-conversations.md
│       ├── 7-memory-and-persistence.md
│       ├── 8-workflows.md
│       ├── 9-chat-user-interface.md
│       └── 10-host-agent.md
├── requirements.txt
├── .env
└── README.md
```

## Workshop Topics

- Introduction to AI agents
- Understanding Microsoft Agent Framework
- Working with GitHub Models
- Tool calling
- MCP integration
- Multi-turn conversations
- Memory and persistence
- Building chat interfaces
- Workflows and orchestration
- Host agent architecture
- Multi-agent workflows
- Deployment basics

## Running the Applications

### Chainlit App

```bash
chainlit run apps/chainlit/app.py
```

### Streamlit App

```bash
streamlit run apps/streamlit/app.py
```

### Additional UI Variants

```bash
# TBD - Instructions for running additional UI variants will be added here.
```

## Recommended VS Code Extensions

//TODO: Add links to extensions

- Python
- Pylance
- Jupyter
- Ruff
- GitHub Copilot

## Resources

- Microsoft Agent Framework  
  <https://learn.microsoft.com/en-us/agent-framework/>
- GitHub Models  
  <https://docs.github.com/en/github-models>
- Chainlit  
  <https://docs.chainlit.io/>
- Streamlit  
  <https://docs.streamlit.io/>
- Model Context Protocol (MCP)  
  <https://modelcontextprotocol.io/introduction>
- Python  
  <https://www.python.org/doc/>
- uv  
  <https://docs.astral.sh/uv/>

## License

MIT License

## Contributing

Contributions, ideas, and improvements are welcome.

Feel free to open issues or submit pull requests.
