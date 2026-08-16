# CLAUDE.md

## Read AGENTS.md first

**[AGENTS.md](AGENTS.md) holds all project rules** — what this workshop is, repo layout,
toolchain, coding standards, testing, docs, git workflow, secrets, and anti-hallucination
constraints. Read it before doing anything in this repo. This file adds only Claude Code
specifics.

When a rule needs to change, edit `AGENTS.md`, not this file.

## Claude Code specifics

- Python work happens in `app/`. Prefer `cd app && uv run <cmd>` over activating a venv.
- The Microsoft Learn MCP server is the best source for Agent Framework APIs. Prefer it over
  recalling from memory — this framework moves fast and class names have changed.
