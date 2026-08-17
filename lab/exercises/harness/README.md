# Exercise 7 — Harness

## Goal

Build OpsAgent's fourth pillar: an agent that works through a *task* rather
than just answering a question — it plans, tracks its own todo list, and
keeps file-backed memory.

## Concepts

- `create_harness_agent(...)` returns an ordinary `Agent`. It is not a
  different runtime — sessions, tools and context providers all still work
  the same way you used them in earlier exercises.
- `harness_instructions` vs `agent_instructions` — the harness gets its own
  instructions about *how to work* (plan, verify, keep todos current),
  separate from the agent's instructions about *what it's for*.
- **A real gotcha, worth knowing.** Left alone, the Harness roots its file
  memory at `Path.cwd() / "agent-file-memory"` — wherever the process happens
  to be run from, not next to this exercise's code. That bit the people
  building this workshop (see the Phase 2 note in
  [`../../../TODO.md`](../../../TODO.md)) — `app/harness.py` pins it under an
  explicit directory instead, and this exercise asks you to do the same.
- `disable_web_search=True` — the Harness enables hosted web search by
  default, but only where the chosen client supports it, which would make
  identical code behave differently on Gemini versus Ollama. Off here for the
  same reason [`app/harness.py`](../../../app/harness.py) turns it off.

## TODOs

Open [`exercise.py`](exercise.py):

1. `create_file_memory()` — build and return a `FileSystemAgentFileStore`
   rooted at `FILE_MEMORY_DIR` (not the default).
2. `create_harness()` — call `create_harness_agent(...)` with a client, a
   name, harness and agent instructions, the file memory store from Step 1,
   and `disable_web_search=True`.

## Run

```bash
cd lab
uv run python -m exercises.harness.exercise "Draft a 3-step plan for adding a health-check endpoint to a Flask app"
```

Look for planning/todo behaviour in the output — that's the harness doing
something `create_ops_agent`-style agents in earlier exercises don't.

## Check yourself

```bash
uv run python -m exercises.harness.solution "Draft a 3-step plan for adding a health-check endpoint to a Flask app"
```

After running it, check `.harness-memory/` appeared next to this file, and
*not* a stray `agent-file-memory/` wherever your shell's cwd was.
