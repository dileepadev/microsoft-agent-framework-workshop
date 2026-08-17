# lab — practice exercises

Seven small exercises, one per capability built in [`app/`](../app/): first
agent, tools, MCP, sessions, memory, workflow, harness. Work through them
after the session, in whichever order you like — each is self-contained.

Every exercise ships two files: `exercise.py`, which has a few `# TODO`
markers for you to fill in, and `solution.py`, a complete reference. Neither
is graded — the only feedback loop is running your own agent and seeing what
it says.

## Setup

```bash
cd lab
uv sync
cp .env.example .env
```

Then open `.env` and fill in one provider block — the same four variables as
`app/`: `LLM_PROVIDER`, `LLM_API_KEY`, `LLM_MODEL`, `LLM_BASE_URL`. If you
already set up `app/.env` during the session, copy those same values across;
`lab/` is a separate `uv` project but reads the identical contract. Run
`uv run python -m providers` to see what each provider needs.

> [!NOTE]
> The `tools` and `harness` exercises call a tool, and not every local model
> can do that. If you're running Ollama, use `llama3.2` or `qwen3:4b` — see
> `.env.example` for the full note.

## Exercises

| # | Exercise | Concept | Run |
| - | -------- | ------- | --- |
| 1 | [`first_agent`](exercises/first_agent/) | Build and run an `Agent` | `uv run python -m exercises.first_agent.exercise "<prompt>"` |
| 2 | [`tools`](exercises/tools/) | Write and attach a custom `@tool` | `uv run python -m exercises.tools.exercise "<prompt>"` |
| 3 | [`mcp`](exercises/mcp/) | Attach the Microsoft Learn MCP server | `uv run python -m exercises.mcp.exercise "<prompt>"` |
| 4 | [`sessions`](exercises/sessions/) | Persist a conversation across restarts | `uv run python -m exercises.sessions.exercise "<prompt>"` |
| 5 | [`memory`](exercises/memory/) | Write a `ContextProvider` | `uv run python -m exercises.memory.exercise` |
| 6 | [`workflow`](exercises/workflow/) | Build a `WorkflowBuilder` pipeline | `uv run python -m exercises.workflow.exercise "<prompt>"` |
| 7 | [`harness`](exercises/harness/) | Build a planning `create_harness_agent` | `uv run python -m exercises.harness.exercise "<prompt>"` |

Each exercise's own `README.md` has the full brief: what to build, which
TODOs to fill in, and what a correct run looks like. Swap `exercise` for
`solution` in any command above to run the finished reference instead.

## Why this is separate from `app/`

`lab/` is its own `uv` project — a different environment, a different
`pyproject.toml`, nothing imported from `app/`. That's deliberate: one broken
install should never take down the rest of the workshop, and an exercise you
solve here shouldn't depend on code you haven't looked at yet. `config.py`
and `providers.py` are the one thing duplicated on purpose — same provider
factory, same fail-loud errors, ported rather than shared, so every exercise
can use whichever provider you picked without `lab/` reaching into `app/`.

## Tests

There isn't a test suite here — the point of a practice lab is the exercise,
not a coverage number. If something won't import, `uv run python -m
exercises.<name>.exercise` will tell you exactly where with a traceback; if
it imports but answers wrong, that's the exercise working as intended.
