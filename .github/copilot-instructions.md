# GitHub Copilot Instructions

## Read AGENTS.md first

**[AGENTS.md](../AGENTS.md) is the single source of truth** for this repository — what this
workshop is, layout, toolchain, coding standards, testing, docs, git workflow, secrets, and
anti-hallucination constraints. This file is a condensed pointer, not a substitute.

Shared rules change in `AGENTS.md`, never here.

## The short version

- Python 3.12 with `uv`, from `app/`. Never `pip install`.
- Run the API with the FastAPI CLI: `uv run fastapi dev api.py`. Not `uvicorn`.
- Only `app/providers.py` may name a model vendor.
- Never hardcode a default model name.
- `lab/`, `docs/` and `src/` are the superseded v1.0 edition — don't copy patterns from them.
