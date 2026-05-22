# OpsAgent — Chainlit

Web chat interface powered by Chainlit — Module 9.

## Run

Workshop command:

```bash
# From lab/:
python -m app.web.chainlit.launcher -w
```

Open <http://localhost:8000> in your browser. Since we use `-w` (watch mode), any code changes will automatically reload the app.

The launcher pins `CHAINLIT_APP_ROOT` to `lab/app/web/chainlit`, so Chainlit keeps its `.chainlit/` and `.files/` folders inside the Chainlit app directory instead of creating them in the current working directory.

Direct Chainlit command also works:

```bash
# From lab/app/web/chainlit/:
chainlit run app.py -w
```

That is a valid way to run the app, and it uses Chainlit exactly as intended. The workshop does not use it as the primary command because most of the workshop is run from `lab/`, and plain `chainlit run ...` uses the current working directory as `CHAINLIT_APP_ROOT`. If you launch it from `lab/`, Chainlit creates `.chainlit/` and `.files/` under `lab/` instead of under `lab/app/web/chainlit/`.

## Workflow command

In the chat input, type:

```text
/workflow production database is down
```

This triggers the Module 8 triage pipeline and returns OpsAgent's resolution steps.

## Features active

| Module | Feature |
| --- | --- |
| Module 4 | Tools — Azure health check, deployment checklist, error diagnosis |
| Module 5 | MCP — Microsoft Learn documentation |
| Module 6 | Multi-turn — session persists for the browser tab lifetime |
| Module 7 | Memory — OpsAgent remembers your name |
| Module 8 | Workflow — `/workflow <query>` command |
