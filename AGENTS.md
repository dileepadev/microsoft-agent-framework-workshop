# AGENTS.md

Canonical instructions for AI coding agents working in this repository.

> This file is the **single source of truth**. `CLAUDE.md` and
> `.github/copilot-instructions.md` intentionally contain only tool-specific notes and point
> back here. Add shared rules **here only** — duplicating them causes drift and contradictory
> guidance.

## What this is

A 60-minute beginner workshop teaching one idea:

> **One agent core. Swap the model, swap the surface, swap the host.**

It exists because GitHub Models was retired on 30 July 2026 and took the previous edition with
it — v1.0 had a single provider welded into the agent, so the shipped workshop cannot be run at
all today. Losing a provider overnight should be a config change, not a rewrite.

The demo agent is **OpsAgent**, an operations assistant. Session format is demo-driven: explain
the concept, show the finished project, walk the build steps. No live coding.

[TODO.md](TODO.md) holds the v2.0 plan and is the place to check what is built and what is not.

## Layout

v2.0 is a rebuild, so most of the repo is still the old edition. Know which is which.

| Path | Status |
| --- | --- |
| `app/` | **v2.0, live.** The demo OpsAgent project — its own `uv` project, with tests |
| `lab/`, `docs/`, `src/`, `public/` | **v1.0, superseded.** Kept until replaced |

Planned but not yet created: `client/` (Streamlit + React surfaces), `website/` (Astro
Starlight), `deploy/`. `lab/` changes meaning in v2.0 — it becomes participant exercises, and the
demo project it holds today moves to `app/`.

> [!IMPORTANT]
> Don't copy patterns from `lab/`, `docs/` or `src/`. That code targets the retired GitHub
> Models endpoint and hardcodes one provider — exactly what this edition exists to undo.

## Toolchain

- Python 3.12, managed with `uv`, from `app/` — `cd app && uv sync`, then `uv run <cmd>`.
  Never `pip install`.
- Optional providers are extras: `uv sync --extra anthropic`, or `--all-extras` for the lot.
- Run the API with the **FastAPI CLI**, not `uvicorn` directly:
  `uv run fastapi dev api.py` while developing, `uv run fastapi run api.py` to serve.
  (`app/api.py` is Phase 4 and not built yet — this is the convention it must follow.)
- Node + npm for the site, once `website/` exists. It will be its own project with its own
  lockfile.

## Coding standards

- Match the style already in the file you're editing.
- Comments explain *why*, not *what*.
- Configuration is four variables — `LLM_PROVIDER`, `LLM_API_KEY`, `LLM_MODEL`, `LLM_BASE_URL`.
  Resist adding a fifth; see [app/config.py](app/config.py).
- **Fail loud, naming the fix.** An unknown provider prints the supported list, a missing
  variable is named alongside what it wants, a missing package prints the `uv sync` command.
- **Never hardcode a default model name.** Provider catalogues churn and a stale default rots
  into an unexplained 404 months later. A test enforces this.
- Only [app/providers.py](app/providers.py) may name a vendor. Nothing in `agent.py`, `tools.py`
  or anything downstream should know which provider is configured.

## Testing

- `cd app && uv run pytest` — offline, no API keys, no network. Run before calling a change done.
- Keep new tests offline. `app/tests/conftest.py` blocks `socket.connect` outright and clears
  every provider variable, so a key in your own `.env` cannot change a result.
- A provider whose package isn't installed skips with the `uv sync --extra` that enables it.
  Green on base dependencies and on `--all-extras` are both valid.

## Docs

- Update [app/README.md](app/README.md) alongside any change to the provider contract.
- Root `README.md` still describes v1.0 and the retired GitHub Models flow. Don't cite it as
  current.

## Git workflow

- Branches: [BRANCH_NAMING_GUIDELINES.md](BRANCH_NAMING_GUIDELINES.md)
- Commits: [COMMIT_MESSAGE_GUIDELINES.md](COMMIT_MESSAGE_GUIDELINES.md) — if the work traces to a
  GitHub issue, reference it (`fixes #12`, `refs #12`); don't invent an issue number if none was
  given. v2.0 work traces to `refs #1`.
- PRs: [PULL_REQUEST_GUIDELINES.md](PULL_REQUEST_GUIDELINES.md)
- Versioning: [VERSIONING.md](VERSIONING.md) — two-part at repo scope, three-part inside modules.

## Secrets

- Real values live in `app/.env` (gitignored) — never in `app/.env.example` or committed
  anywhere.
- Participants bring their own key for whichever provider they pick. Don't add a shared or
  fallback key anywhere.

## Anti-hallucination

Package and module names in this ecosystem are not what the documentation implies. These were
confirmed against the installed packages:

- Gemini is **`agent-framework-gemini`** / `agent_framework.gemini`. There is no usable
  `agent-framework-google` — that name is a placeholder on PyPI, and `agent_framework.google`
  holds the Anthropic-on-Vertex client instead.
- Bedrock is **`agent_framework.amazon`**, not `agent_framework.bedrock`.
- Importing a provider namespace **succeeds without its package installed** — core registers a
  lazy stub that only raises when a class is read off it. Any availability check must reach the
  class, not the module.
- The `agent-framework` meta-package resolves to `agent-framework-core[all]` and pulls every
  integration Microsoft ships. `app/` depends on core plus named providers instead.

Unsure whether a package, class, or model name is real? Check it against the installed package
or the Microsoft Learn MCP server, and say so rather than guessing.
