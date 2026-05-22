# Introduction

Welcome to the **Microsoft Agent Framework Workshop** — a hands-on guide to building production-ready AI agents in Python.

## What Is Microsoft Agent Framework?

[Microsoft Agent Framework](https://learn.microsoft.com/agent-framework) is an open-source Python SDK for building, orchestrating, and hosting AI agents. It provides first-class support for:

- **Tool calling** — attach any Python function as an agent tool
- **MCP (Model Context Protocol)** — connect agents to live external data sources
- **Multi-turn conversations** — built-in history and memory providers
- **Multi-agent workflows** — orchestrate agents into pipelines
- **Hosting** — deploy agents via Azure Functions, A2A, OpenAI-compatible, or AG-UI endpoints

## What You Will Build

This workshop guides you through building **OpsAgent** — an AI-powered operations and engineering assistant — from a blank Python project to a fully hosted HTTP endpoint.

Each module builds directly on the previous one. By the end you will have a single agent that uses tools, retrieves live documentation via MCP, remembers conversation history, participates in multi-agent workflows, runs inside multiple chat UIs, and is deployed as a serverless Azure Function.

## Who This Workshop Is For

| Background | What You Will Learn |
| --- | --- |
| Python developers new to AI agents | How to build and run your first agent |
| Cloud / DevOps engineers | How to wire tools, MCP, and host agents |
| AI/ML engineers | How to compose multi-agent workflows |

No prior experience with Azure or AI agents is required — just Python 3.10+ and a GitHub account.

## Workshop Structure

The workshop is split into 10 modules under **Getting Started**:

| Module | Topic |
| --- | --- |
| 1 | Environment Setup |
| 2 | GitHub Models Connection |
| 3 | Microsoft Agent Framework Agents |
| 4 | Tool Calling |
| 5 | MCP Integration |
| 6 | Multi-Turn Conversations |
| 7 | Memory & Persistence |
| 8 | Workflows |
| 9 | Chat User Interface |
| 10 | Host Agent |

Each module has a corresponding test file in `lab/` so you can validate each step independently before moving on.

## Key Technologies

| Technology | Role |
| --- | --- |
| [Microsoft Agent Framework](https://learn.microsoft.com/agent-framework) | Core agent SDK |
| [GitHub Models](https://github.com/marketplace/models) | Free LLM inference (GPT-4o mini) |
| [MCP — Model Context Protocol](https://modelcontextprotocol.io) | Live data retrieval |
| [Azure Functions](https://learn.microsoft.com/azure/azure-functions) | Serverless agent hosting |
| [Azurite](https://learn.microsoft.com/azure/storage/common/storage-use-azurite) | Local Azure Storage emulator |

## Before You Start

Head to [Module 1 — Environment Setup](getting-started/1-environment-setup) to configure your local development environment.

!!! tip "GitHub Token"
    You will need a GitHub Personal Access Token with **Models** permission enabled. Create one at [github.com/settings/tokens](https://github.com/settings/tokens).
