# Exercise 1 — Your first agent

## Goal

Build the smallest possible agent from the shared provider factory and ask it
one question.

## Concepts

- `create_chat_client()` from [`providers.py`](../../providers.py) — reads
  `LLM_PROVIDER` and friends from `lab/.env` and hands back the right chat
  client, whichever provider you picked. Nothing downstream needs to know
  which one.
- `Agent(client=..., name=..., instructions=...)` — the object that answers
  questions. `name` and `instructions` are the whole personality.
- `await agent.run(prompt)` — runs one turn and returns a result whose
  `.text` is the answer.

This is the layer underneath everything else in the lab. The finished,
fully-loaded version — tools, MCP, memory, all attached — is
[`app/agent.py`](../../../app/agent.py); this exercise is just the client,
the name, the instructions and one call.

## TODOs

Open [`exercise.py`](exercise.py):

1. `create_agent()` — build and return an `Agent` using `create_chat_client()`.
2. `ask()` — call `agent.run(prompt)` and return `.text`.

## Run

```bash
cd lab
uv run python -m exercises.first_agent.exercise "What is Azure App Service, in one sentence?"
```

## Check yourself

```bash
uv run python -m exercises.first_agent.solution "What is Azure App Service, in one sentence?"
```

Same question, both should produce a reasonable one-paragraph answer — the
exact wording will differ by provider and run.
