# client — agent usage surfaces

> [!NOTE]
> Placeholder. Built in Phase 4 — see [TODO.md](../TODO.md).

Two front ends onto the same agent, so *swap the surface* is a real demonstration
rather than a claim:

| Folder | Stack | Environment |
| --- | --- | --- |
| [streamlit/](streamlit/) | Python | its own `uv` project |
| [web/](web/) | Vite + React | its own npm project |

Both talk to the same `app/api.py` and are configured by a single API base URL,
so either can point at a local or a deployed agent. Participants pick whichever
they prefer.
