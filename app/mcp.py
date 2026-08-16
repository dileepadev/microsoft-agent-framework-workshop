"""
Microsoft Learn MCP — the one integration carried over intact from v1.0.

MCP is why this survived the rewrite. The Learn server is hosted by Microsoft
and needs no key, so it works identically for every participant no matter which
model provider they picked — which is the same lesson as `providers.py`, applied
to tools instead of models.

The tool connects lazily. Constructing it opens nothing; the agent establishes
the session on first use, which is why an agent holding MCP tools should be used
as an async context manager so the connection is closed again:

    async with create_ops_agent() as agent:
        result = await agent.run("How do I configure health checks on App Service?")
"""

from __future__ import annotations

from agent_framework import MCPStreamableHTTPTool

LEARN_MCP_NAME = "Microsoft Learn MCP"
LEARN_MCP_URL = "https://learn.microsoft.com/api/mcp"


def create_learn_mcp(*, approval_mode: str = "never_require") -> MCPStreamableHTTPTool:
    """
    Build the Microsoft Learn MCP tool.

    Args:
        approval_mode: `"never_require"` keeps the demo moving. The server is
            read-only — it searches and fetches documentation — so there is
            nothing to confirm. A server that could change state deserves
            `"always_require"`.
    """
    return MCPStreamableHTTPTool(
        name=LEARN_MCP_NAME,
        url=LEARN_MCP_URL,
        approval_mode=approval_mode,
    )
