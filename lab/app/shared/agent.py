"""
Shared agent factory — Module 9.

Brings together every workshop module into a single reusable factory:

  Module 4 — Tool Calling:     tools from shared/tools.py
  Module 5 — MCP Integration:  MCPStreamableHTTPTool from shared/mcp.py
  Module 6 — Multi-Turn:       InMemoryHistoryProvider
  Module 7 — Memory:           UserMemoryProvider from shared/providers.py
  Module 8 — Workflow:         executors and builder from shared/workflow.py
"""

from openai import AsyncOpenAI

from agent_framework import (
    Agent,
    InMemoryHistoryProvider,
)
from agent_framework.openai import OpenAIChatCompletionClient

from .mcp import create_learn_mcp
from .providers import UserMemoryProvider
from .tools import check_azure_service_health, diagnose_error, get_deployment_checklist
from .workflow import build_triage_workflow, classify_severity

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

GITHUB_BASE_URL = "https://models.github.ai/inference"

OPSAGENT_NAME = "OpsAgent"
OPSAGENT_DESCRIPTION = "OpsAgent is an AI-powered operations and engineering assistant."
OPSAGENT_INSTRUCTIONS = (
    "You are OpsAgent, an AI-powered operations and engineering assistant. "
    "Help developers and cloud engineers troubleshoot issues, retrieve documentation, "
    "analyze systems, and automate operational workflows. "
    "Use the available tools when relevant. Keep responses concise, actionable, and practical."
)

# ---------------------------------------------------------------------------
# Client factory
# ---------------------------------------------------------------------------


def create_chat_client(
    github_token: str, github_model: str
) -> OpenAIChatCompletionClient:
    """Create an OpenAIChatCompletionClient backed by GitHub Models."""
    async_openai = AsyncOpenAI(
        api_key=github_token,
        base_url=GITHUB_BASE_URL,
    )
    return OpenAIChatCompletionClient(
        model=github_model,
        async_client=async_openai,
    )


# ---------------------------------------------------------------------------
# Agent factory  (Modules 4 + 5 + 6 + 7 combined)
# ---------------------------------------------------------------------------


def create_ops_agent(client: OpenAIChatCompletionClient) -> Agent:
    """
    Create OpsAgent with all workshop features active:

      Tools (Module 4)       — Azure health, deployment checklist, error diagnosis
      MCP   (Module 5)       — Microsoft Learn documentation
      Multi-turn (Module 6)  — InMemoryHistoryProvider
      Memory (Module 7)      — UserMemoryProvider

    Usage (CLI / long-lived process):
        async with create_ops_agent(client) as agent:
            session = agent.create_session()
            result = await agent.run(query, session=session)

    Usage (per-request / web):
        agent = create_ops_agent(client)
        session = agent.create_session()
        result = await agent.run(query, session=session)
    """
    return Agent(
        client=client,
        name=OPSAGENT_NAME,
        description=OPSAGENT_DESCRIPTION,
        instructions=OPSAGENT_INSTRUCTIONS,
        tools=[
            check_azure_service_health,
            get_deployment_checklist,
            diagnose_error,
            create_learn_mcp(),
        ],
        context_providers=[
            UserMemoryProvider(),
            InMemoryHistoryProvider(load_messages=True),
        ],
    )
