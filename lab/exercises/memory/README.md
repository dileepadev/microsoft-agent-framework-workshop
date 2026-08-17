# Exercise 5 — Memory

## Goal

Write a `ContextProvider` that tracks something across turns *without* it
being part of the visible conversation transcript — here, how many questions
the user has asked this session — and injects that as an instruction before
every model call.

## Concepts

- **History vs. memory.** History is the transcript; a `HistoryProvider`
  replays it. Memory is a fact kept *out* of the transcript and re-injected
  as an instruction on every turn. `ContextProvider` is the base for the
  second kind, and that's what this exercise builds.
- `before_run(*, agent, session, context, state)` — runs ahead of the model
  call. Read from `state` and call `context.extend_instructions(source_id,
  text)` to add an instruction.
- `after_run(*, agent, session, context, state)` — runs after the model call.
  Write back to `state` whatever you learned this turn.
- `state` is a plain `dict` that belongs to the session. It resets with a new
  session — pairing a `ContextProvider` with `FileSessionStore` (Exercise 4)
  is what makes memory survive a restart; on its own it only lasts as long as
  the session object does.

See [`app/memory.py`](../../../app/memory.py)'s `UserMemoryProvider` for a
different worked example of the same pattern (it remembers the user's name
via a regex instead of a counter).

## TODOs

Open [`exercise.py`](exercise.py):

1. `QuestionCounterMemory.before_run()` — read `state.get("count", 0)` and
   inject an instruction telling the model which question number this is.
2. `QuestionCounterMemory.after_run()` — increment `state["count"]`.

## Run

```bash
cd lab
uv run python -m exercises.memory.exercise
```

With no arguments it runs three prompts in a row against the same in-memory
session. Watch the answers (or add a print of the instruction) shift once the
count climbs — a correct implementation can, for example, have the agent
mention "third question" by the third turn if your instruction text says so.

## Check yourself

```bash
uv run python -m exercises.memory.solution
```
