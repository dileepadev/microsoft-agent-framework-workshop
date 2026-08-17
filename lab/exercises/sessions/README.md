# Exercise 4 — Sessions

## Goal

Make a conversation survive a restart. Run this script twice, and the second
run should know what you said in the first — because it's a new process that
reloads the conversation from disk rather than remembering anything itself.

## Concepts

- `AgentSession` — the object that carries a conversation's transcript across
  calls to `agent.run(prompt, session=session)`.
- `FileSessionStore(storage_path=...)` — persists a session's *state* to disk
  by id, separate from the agent itself. You save and load it yourself, which
  is what lets a later process (or a web request carrying a session id) pick
  a conversation back up.
- `agent.create_session(session_id=...)` — starts a fresh session under a
  chosen id, used when the store has nothing for that id yet.

This exercise covers the session-persistence half of what
[`app/memory.py`](../../../app/memory.py) does. The other half — remembering
a *fact* like the user's name, as opposed to the raw transcript — is
Exercise 5.

## TODOs

Open [`exercise.py`](exercise.py):

1. `create_store()` — build a `FileSessionStore` rooted at `STORAGE_DIR`
   (create the directory first if it's missing).
2. `resume_or_create()` — look up the session id in the store; if it's there,
   return it, otherwise start a new session on the agent with that id.
3. `save()` — write the session's state back to the store after the turn.

## Run

Two separate commands, same fixed session id under the hood:

```bash
cd lab
uv run python -m exercises.sessions.exercise "my name is Sam, remember it"
uv run python -m exercises.sessions.exercise "what did I say my name was?"
```

The second command is a brand-new process. If Steps 1–3 are right, it answers
correctly anyway — everything it needs is sitting in `.sessions/` next to
this file.

## Check yourself

```bash
uv run python -m exercises.sessions.solution "my name is Sam, remember it"
uv run python -m exercises.sessions.solution "what did I say my name was?"
```
