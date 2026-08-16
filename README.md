# Microsoft Agent Framework Workshop

A 60-minute workshop that builds **OpsAgent**, an AI-powered operations assistant, with
Microsoft Agent Framework — and teaches one idea:

> **One agent core. Swap the model, swap the surface, swap the host.**

- Live workshop site: <https://dileepadev.github.io/microsoft-agent-framework-workshop/>
- Plan and progress: [TODO.md](TODO.md)

## Status: v2.0 in progress

**GitHub Models was retired on 30 July 2026.** The playground, model catalog and inference API
are gone for everyone. The entire v1.0 lab ran against `https://models.github.ai/inference`, so
that edition cannot be run at all today.

v2.0 is a **new workshop**, not an upgrade. The OpsAgent scenario and the Microsoft Learn MCP
integration carry over; everything else is rebuilt. Losing a provider overnight should be a
config change, not a rewrite — which is exactly what the framework is for, and now the lesson of
the session.

The site linked above still serves the v1.0 content until the v2.0 rebuild lands.

## Repository structure

| Folder | Purpose | Status |
| --- | --- | --- |
| [app/](app/) | The demo OpsAgent project — own `uv` project | **Built** |
| [website/](website/) | Teaching content and presentation — own npm project | v1.0 content, rebuild pending |
| [lab/](TODO.md) | Participant practice exercises — own `uv` project | Not yet built |
| [client/](client/) | Agent usage surfaces: Streamlit and Vite + React | Not yet built |
| [deploy/](deploy/) | Render, Docker and Azure hosting | Not yet built |
| [docs/](docs/) | Facilitator materials | Not yet built |

Each project folder carries its own isolated environment, so one broken install cannot take down
the rest of the workshop.

## Quick start

Run the agent:

```bash
cd app
uv sync
cp .env.example .env     # then add a key for one provider
uv run python -m agent "What should I check before deploying a Container App?"
```

The default provider is Google AI Studio, which has a free tier and needs no card. To see every
supported provider and what each one requires:

```bash
cd app && uv run python -m providers
```

Run the site:

```bash
cd website
npm install
npm run dev
```

## Choosing a provider

The agent code is identical for every provider — only `.env` changes. Four variables configure
all of them:

| Variable | Meaning |
| --- | --- |
| `LLM_PROVIDER` | Which provider to use |
| `LLM_API_KEY` | The credential |
| `LLM_MODEL` | The model or deployment id |
| `LLM_BASE_URL` | The endpoint, where one is needed |

Supported: Google AI Studio, OpenAI, Azure OpenAI, Anthropic, Ollama, Microsoft Foundry, Foundry
Local, Amazon Bedrock, and an `openai-compatible` catch-all that reaches OpenRouter, Groq,
Cerebras, Together, Fireworks, DeepSeek, xAI, LM Studio and vLLM.

Free tiers worth knowing about now that GitHub Models is gone: Google AI Studio, Groq, Cerebras,
OpenRouter and Mistral. Ollama and Foundry Local need no key at all.

See [app/README.md](app/README.md) for the full detail.

## Prerequisites

- Python 3.12 and [`uv`](https://docs.astral.sh/uv/)
- Node.js and npm, for the website
- An API key for one provider, or [Ollama](https://ollama.com) to run fully offline
- Basic Python knowledge

## Tech stack

Microsoft Agent Framework · MCP · FastAPI · Streamlit · Vite + React · Astro · Tailwind CSS ·
`uv`

## Resources

- Microsoft Agent Framework: <https://learn.microsoft.com/agent-framework/>
- Model Context Protocol: <https://modelcontextprotocol.io/introduction>
- Astro: <https://docs.astro.build/>
- uv: <https://docs.astral.sh/uv/>

## Contributing

Issues and pull requests are welcome. Please read
[CONTRIBUTING.md](CONTRIBUTING.md), [BRANCH_NAMING_GUIDELINES.md](BRANCH_NAMING_GUIDELINES.md),
[COMMIT_MESSAGE_GUIDELINES.md](COMMIT_MESSAGE_GUIDELINES.md) and
[PULL_REQUEST_GUIDELINES.md](PULL_REQUEST_GUIDELINES.md) first.

## License

MIT License. See [LICENSE](LICENSE).
