"""
MCP tool factory — Module 5.

Provides the Microsoft Learn MCP tool used by OpsAgent.
"""

from agent_framework import MCPStreamableHTTPTool


def create_learn_mcp() -> MCPStreamableHTTPTool:
    """Return the Microsoft Learn MCP tool (Module 5)."""
    return MCPStreamableHTTPTool(
        name="Microsoft Learn MCP",
        url="https://learn.microsoft.com/api/mcp",
        approval_mode="never_require",
    )
