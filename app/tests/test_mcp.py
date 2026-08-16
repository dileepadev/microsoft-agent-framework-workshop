"""
Microsoft Learn MCP tests.

These check wiring, not the server. Nothing here talks to Microsoft Learn — the
`no_network` fixture would fail the test if it tried — so what is proved is that
the tool is constructed correctly and attached where the framework expects it.
"""

from __future__ import annotations

from agent_framework import MCPStreamableHTTPTool

from mcp import LEARN_MCP_NAME, LEARN_MCP_URL, create_learn_mcp


def test_points_at_the_hosted_learn_server():
    """The URL is the whole integration — a typo here fails only at runtime."""
    assert LEARN_MCP_URL == "https://learn.microsoft.com/api/mcp"

    tool = create_learn_mcp()
    assert isinstance(tool, MCPStreamableHTTPTool)
    assert tool.name == LEARN_MCP_NAME


def test_constructing_the_tool_opens_no_connection():
    """
    Construction must stay lazy.

    If it connected here, importing the app would need working network, and
    every offline test in this suite would break.
    """
    create_learn_mcp()  # the no_network fixture asserts this


def test_tool_is_an_async_context_manager():
    """Which is why agents holding MCP tools are used with `async with`."""
    tool = create_learn_mcp()
    assert hasattr(tool, "__aenter__")
    assert hasattr(tool, "__aexit__")


def test_approval_mode_is_configurable():
    """Read-only by default; a stateful server should require approval."""
    assert create_learn_mcp(approval_mode="always_require") is not None
