# Exercise 2 — Tools

## Goal

Write a custom `@tool` function and attach it to an agent, so the model can
call real Python instead of guessing an answer.

## Concepts

- `@tool(approval_mode="never_require")` — turns a plain function into
  something an agent can call. `"never_require"` is right for a read-only
  tool that computes a number; a tool that writes, deploys or deletes should
  use `"always_require"` so a human confirms the call first.
- `Annotated[T, Field(description=...)]` — how a tool's parameters get
  descriptions the model can read, exactly like a docstring for a human.
- `Agent(..., tools=[your_tool])` — attaching one or more tools to an agent.

See [`app/tools.py`](../../../app/tools.py) for three worked examples in this
same style (`check_azure_service_health`, `get_deployment_checklist`,
`diagnose_error`), and [`app/agent.py`](../../../app/agent.py) for how
`OPSAGENT_TOOLS` gets passed to `Agent(tools=...)`.

## The tool to build

`estimate_monthly_cost(hourly_rate: float, hours_per_day: float = 24) -> str`

Given an hourly compute rate and how many hours a day the resource runs,
return a one-line string with the estimated monthly cost (30 days). This is
deterministic arithmetic, not a model call — the same argument `app/tools.py`
makes for its own tools: a number the agent can be wrong about is worse than
no number at all.

## TODOs

Open [`exercise.py`](exercise.py):

1. `estimate_monthly_cost()` — decorate it with `@tool(...)`, annotate both
   parameters with `Field(description=...)`, give `hours_per_day` a default
   of `24`, and return a formatted string (not a bare float — the model has
   to read this back to the user).
2. `create_agent()` — build an `Agent` with this tool attached.

## Run

```bash
cd lab
uv run python -m exercises.tools.exercise "What's the monthly cost of a VM at \$0.05/hour running 24 hours a day?"
```

Ask it to compare a couple of rates in one prompt — if it's wired up
correctly, the agent calls the tool once per number rather than doing the
arithmetic itself.

## Check yourself

```bash
uv run python -m exercises.tools.solution "What's the monthly cost of a VM at \$0.05/hour running 24 hours a day?"
```
