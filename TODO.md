# TODO

This file tracks tasks, improvements, and features planned for upcoming updates or releases of this repository.  

>[!Note]
> This list is **not exhaustive** and may change over time. Items are not necessarily in priority order.

## Upcoming Tasks

Planned for **v2.0** ([#1](https://github.com/dileepadev/microsoft-agent-framework-workshop/issues/1)).

v2.0 is a **new workshop**, not an upgrade of v1.0. The OpsAgent scenario and the
Microsoft Learn MCP integration carry over; everything else is rebuilt.

### Why this release exists

**GitHub Models was retired on 30 July 2026.** The playground, model catalog,
inference API and BYOK are gone for every customer, including existing ones. The
entire v1.0 lab ran against `https://models.github.ai/inference`, so the shipped
workshop **cannot be run at all today**.

That is also the lesson of the new session. Losing a provider overnight should be
a config change, not a rewrite — which is exactly what the framework is for.

### The thesis

> **One agent core. Swap the model, swap the surface, swap the host.**

Every module serves that one idea, and it gives the session title its meaning.

### Session shape

60 minutes, beginner audience, demo-driven — explain the concept, show the
finished project, then walk the build steps. No live coding.

---

## Structure

Four project folders, each with its own isolated environment so one broken
install can never take down the rest of the workshop, plus `deploy/` and `docs/`
which are plain files with no environment of their own.

>[!Important]
> `lab/` changes meaning in v2.0. In v1.0 it held the entire application; here it
> holds only the participant exercises, and the demo project moves to `app/`.
> Anyone returning from v1.0 will expect the old layout.

| Folder | Purpose | Environment |
| --- | --- | --- |
| `lab/` | Participant practice exercises | own `uv` project |
| `app/` | The demo OpsAgent project | own `uv` project |
| `client/` | Agent usage surfaces | `streamlit/` own `uv`; `web/` own npm |
| `website/` | Learn, build and presentation content | own npm |

```md
├── lab/                    # practice — one exercise per capability
├── app/                    # the demo agent
│   ├── config.py           # env loading, fails loud at startup
│   ├── providers.py        # chat-client factory  ← the star of the workshop
│   ├── agent.py            # OpsAgent
│   ├── tools.py            # @tool functions
│   ├── mcp.py              # Microsoft Learn MCP   (carried over from v1.0)
│   ├── memory.py           # sessions + context providers
│   ├── workflow.py         # triage workflow
│   ├── harness.py          # Agent Harness
│   ├── api.py              # FastAPI — the surface both clients talk to
│   └── tests/
├── client/
│   ├── streamlit/          # Python client
│   └── web/                # Vite + React client
├── website/                # Astro Starlight
│   └── public/slides/      # standalone deck: index.html + assets/{css,js,img}
├── deploy/                 # render.yaml, Dockerfile, azure/
└── docs/                   # facilitator materials
```

Participants pick whichever client they prefer — both talk to the same
`app/api.py`, which is the point.

---

## Provider support

The agent code is **identical** for every provider. Only the client changes.
Participants choose whatever they have a key for, or run fully local.

- [ ] Build `app/providers.py` as a factory keyed on `LLM_PROVIDER`, with `LLM_API_KEY`, `LLM_MODEL` and `LLM_BASE_URL`.
- [ ] Fail loudly at startup on an unknown provider or a missing variable, naming the exact variable to set.
- [ ] Cover the dedicated clients: Microsoft Foundry (`FoundryChatClient`), OpenAI and Azure OpenAI (`OpenAIChatClient`), Google AI Studio (`GeminiChatClient`), Anthropic (`AnthropicClient`), Ollama (`OllamaChatClient`), Foundry Local (`FoundryLocalClient`), Amazon Bedrock.
- [ ] Add an `openai-compatible` catch-all using `OpenAIChatClient(base_url=...)`, which reaches OpenRouter, Groq, Cerebras, Together, Fireworks, DeepSeek, xAI, LM Studio, vLLM and anything else OpenAI-shaped.
- [ ] Note which packages still need `--pre`: Gemini, Ollama, Anthropic and Foundry Local are beta; `agent-framework-openai` and `agent-framework-foundry` are GA.
- [ ] Default the demo to Google AI Studio, with Ollama as the offline fallback for unreliable conference wifi.
- [ ] Write `website` guidance on free tiers now that GitHub Models is gone: Google AI Studio, Groq, Cerebras, OpenRouter, Mistral, and the fully local runtimes.
- [ ] Do not hardcode default model names for providers whose catalogues churn — a stale name produces a confusing 404 months later.

## Phase 1 — Agent core

- [ ] Scaffold `app/` as its own `uv` project on `agent-framework>=1.14.0`.
- [ ] `config.py`: explicit `load_dotenv()` — the framework does **not** auto-load `.env` any more.
- [ ] `agent.py`: OpsAgent built from the provider factory.
- [ ] `tools.py`: operational `@tool` functions (service health, deployment checklist, error diagnosis).
- [ ] `tests/test_providers.py`: every provider resolves a client without network access.
- [ ] Pin dependencies. Do not ship an unpinned `requirements.txt` alongside a pinned `pyproject.toml` as v1.0 did.

## Phase 2 — Capabilities

- [ ] Port the Microsoft Learn MCP integration from v1.0 (`https://learn.microsoft.com/api/mcp`).
- [ ] Multi-turn conversation with `AgentSession`.
- [ ] Memory via `ContextProvider`. Either implement real file-backed persistence or state plainly that it is in-memory — v1.0 promised SQLite and Cosmos on the slides and shipped neither.
- [ ] Triage workflow with `WorkflowBuilder`.
- [ ] **Agent Harness** — new since v1.0 (landed 1.7.0) and now a fourth pillar beside Agents, Workflows and Integrations. Planning and todos, context compaction, file memory, tool approval, observability.

## Phase 3 — Practice lab

The exercises participants work through afterwards, mirroring the capabilities in
`app/` one at a time.

- [ ] Scaffold `lab/` as its own `uv` project, independent of `app/`.
- [ ] One self-contained exercise per capability: first agent, tools, MCP, sessions, memory, workflow, harness.
- [ ] Each exercise runnable on its own, with the provider factory shared so a participant can use whichever provider they picked.
- [ ] Include a worked solution for each exercise.
- [ ] Give `lab/` a real README. v1.0 shipped a 0-byte one that `pyproject.toml` still referenced.

## Phase 4 — Client surfaces

- [ ] `app/api.py`: FastAPI with streaming and multi-turn session handling.
- [ ] `client/streamlit/`: own `uv` project.
- [ ] `client/web/`: Vite + React, own npm project, deployable as static files.
- [ ] Both clients configured by a single API base URL so either can point at local or deployed.

## Phase 5 — Deployment

Participants pick a host, same as they pick a provider.

- [ ] `deploy/render.yaml` and a Dockerfile.
- [ ] Guides for Render, FastAPI Cloud, Azure Container Apps, Azure Functions, and Foundry Hosted Agents (now GA, via `azd ai agent init → run → provision → deploy`).
- [ ] Client deployment to GitHub Pages and Vercel.
- [ ] GitHub Actions workflows for the site and at least one agent host.
- [ ] Document environment variables per host, and never commit a `.env`.

## Phase 6 — Website

- [ ] Rebuild on **Astro Starlight** with Tailwind v4, replacing v1.0's hand-rolled Astro and legacy Tailwind v3 integration.
- [ ] Sidebar sections: Learn, Build, Stack, Deploy, Presentation.
- [ ] Write content as MDX content collections.
- [ ] Keep the v1.0 theme, branding and QR assets.
- [ ] Add a Mermaid component for architecture diagrams.

## Phase 7 — Deck and facilitator docs

- [ ] Rebuild the deck as standalone `website/public/slides/index.html` with external CSS and JS, replacing v1.0's 3,810-line `presentation.astro` monolith.
- [ ] Include progress bar, slide counter, overview mode, presenter notes and a **timer** — the timer matters for holding 60 minutes.
- [ ] Derive the slide counter from the DOM. v1.0 hardcoded `1 / 17` against 22 actual slides.
- [ ] Open on the GitHub Models retirement, then the four pillars.
- [ ] Add a "what's new" slide: Go SDK in public preview, Foundry Hosted Agents GA, and Foundry retiring its own Workflows on 1 December 2026 in favour of Agent Framework.
- [ ] Write `docs/`: run-of-show, session brief, prerequisites checklist, facilitator prep, free-tier notes.
- [ ] In the run-of-show, decide the drop order in advance. Covering the full arc in 60 minutes is tight even when narrating pre-built code, and if a block overruns it is deployment — the payoff in the session title — that gets squeezed. Agent Harness is the cheapest cut, reducible to a single slide.

## Phase 8 — Release

- [ ] Fill in the `## [2.0]` section of `CHANGELOG.md`.
- [ ] Update issue [#1](https://github.com/dileepadev/microsoft-agent-framework-workshop/issues/1) with the final scope.
- [ ] Correct the v1.0 changelog entry, which claims "two deployed frontends" where the repo has four and none deployed.
- [ ] Commit the community standards files.
- [ ] Set an initial version in each module manifest (`app/`, `lab/`, `client/streamlit/`, `client/web/`, `website/`) per [VERSIONING.md](VERSIONING.md).
- [ ] Tag the repository release `v2.0` — two-part at repo scope, three-part inside modules.

---

## Verification

- [ ] `uv sync` succeeds independently in `lab/`, `app/` and `client/streamlit/`.
- [ ] `pytest` green in `app/`.
- [ ] Work through one `lab/` exercise start to finish against a clean environment, using only the written instructions.
- [ ] Live smoke against at least two real providers — same prompt, same tools, both answer.
- [ ] MCP module returns real Microsoft Learn results.
- [ ] `uvicorn app.api:app` with both clients holding a multi-turn conversation.
- [ ] Deploy to one host from a clean clone using only the written guide.
- [ ] `npm run build` clean in `website/`, every sidebar link resolving.
- [ ] Read the deck against its own timer to confirm 60 minutes holds.
