# Exercise 6 — Workflow

## Goal

Build a three-step `WorkflowBuilder` pipeline — a deterministic step, an
agent step, a deterministic step — that routes a support message to the
right topic before an agent answers it.

    tag_input  →  SupportAgent  →  capture_output

## Concepts

- `@executor(id=...)` — turns a plain async function into a workflow step.
  `await ctx.send_message(...)` passes its result to the next step.
- **Deterministic steps bookend the model call.** Topic classification is a
  keyword match, not a model call — reproducible, free, and it can't
  hallucinate a topic. That's the same argument
  [`app/workflow.py`](../../../app/workflow.py) makes for severity
  classification; this exercise applies it to a different routing decision.
- `WorkflowBuilder(start_executor=..., output_from=[...]).add_edge(a,
  b).add_edge(b, c).build()` — wires the three steps into a `Workflow`.
- Running it: `events = await workflow.run(message)`, then
  `events.get_outputs()` returns a list of whatever `ctx.yield_output(...)`
  produced.

## TODOs

Open [`exercise.py`](exercise.py):

1. `classify_topic()` — return `"BILLING"` if any billing keyword appears in
   the message (case-insensitive), `"TECHNICAL"` if any technical keyword
   appears, otherwise `"GENERAL"`. Check billing first, so a message
   mentioning both reads as the more specific topic.
2. `tag_input()` — send `f"[{classify_topic(message)}] {message}"` onward.
3. `capture_output()` — yield `response.agent_response.text` as the
   workflow's output.
4. `build_support_workflow()` — build the `SupportAgent` and wire
   `tag_input → agent → capture_output`.

## Run

```bash
cd lab
uv run python -m exercises.workflow.exercise "I was charged twice for my subscription this month"
```

Try a technical one too: `"the API keeps returning 500 errors"`.

## Check yourself

```bash
uv run python -m exercises.workflow.solution "I was charged twice for my subscription this month"
```
