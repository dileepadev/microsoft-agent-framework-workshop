# Exercise 3 — MCP

## Goal

Attach the hosted Microsoft Learn MCP server to an agent as a tool, so it can
search and fetch real documentation instead of recalling it from training
data.

## Concepts

- `MCPStreamableHTTPTool(name=..., url=..., approval_mode=...)` — wraps a
  remote MCP server as a tool an agent can call.
- The Learn server is hosted by Microsoft and needs no key, so it works the
  same for every provider — the same "swap the model, not the code" idea
  `providers.py` applies to models, applied here to tools.
- **Lazy connection.** Constructing the tool opens nothing; the agent opens
  the connection on first use. That is why an agent holding an MCP tool must
  be used as an **async context manager** (`async with ... as agent:`) so the
  connection gets closed again.

See [`app/mcp.py`](../../../app/mcp.py) for the version this exercise mirrors.

## TODOs

Open [`exercise.py`](exercise.py):

1. `create_learn_mcp()` — build and return an `MCPStreamableHTTPTool` pointed
   at `https://learn.microsoft.com/api/mcp`.
2. `create_agent()` — build an `Agent` with that tool attached.
3. `main()` — open the agent with `async with`, then run the prompt inside
   the `with` block.

## Run

```bash
cd lab
uv run python -m exercises.mcp.exercise "How do I configure health checks on Azure App Service?"
```

## Check yourself

```bash
uv run python -m exercises.mcp.solution "How do I configure health checks on Azure App Service?"
```

A correct answer should read like it came from real Learn documentation
(specific settings, paths, portal steps) rather than a generic explanation.
