# client/streamlit — Python client

> [!NOTE]
> Placeholder. Built in Phase 4 — see [TODO.md](../../TODO.md).

A Streamlit chat UI for OpsAgent, as its own `uv` project. Talks to `app/api.py`
over HTTP — it does not import the agent directly, which is what keeps the agent
swappable underneath it.
