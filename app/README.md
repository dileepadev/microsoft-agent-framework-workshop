# app — OpsAgent

The demo agent for the workshop, and the answer to the question that forced this
edition: **GitHub Models was retired on 30 July 2026 and took v1.0 with it.**

That happened because v1.0 had one provider welded into the agent. This project
is built the other way round:

> **One agent core. Swap the model, swap the surface, swap the host.**

Swapping the model is a change to `.env`. No code moves.

## Layout

| File | What it does |
| --- | --- |
| [config.py](config.py) | Loads `.env`, resolves the four `LLM_*` variables |
| [providers.py](providers.py) | The provider factory — the only file that knows a vendor exists |
| [agent.py](agent.py) | OpsAgent |
| [tools.py](tools.py) | `@tool` functions |
| [tests/](tests/) | Runs offline, with sockets blocked |

## Setup

```bash
cd app
uv sync
cp .env.example .env
```

Then open `.env` and fill in one provider block. The default is Google AI Studio,
which has a free tier and no card requirement — get a key at
[aistudio.google.com/apikey](https://aistudio.google.com/apikey).

Ask it something:

```bash
uv run python -m agent "What should I check before deploying a Container App?"
```

## Configuration

Four variables configure every provider:

| Variable | Meaning |
| --- | --- |
| `LLM_PROVIDER` | Which provider to use — always required |
| `LLM_API_KEY` | The credential — most providers |
| `LLM_MODEL` | The model or deployment id — always required |
| `LLM_BASE_URL` | The endpoint — some providers |

To see which of those a given provider needs:

```bash
uv run python -m providers
```

### Providers

| `LLM_PROVIDER` | Client | Install |
| --- | --- | --- |
| `google` | `GeminiChatClient` | `uv sync` |
| `openai` | `OpenAIChatClient` | `uv sync` |
| `azure-openai` | `OpenAIChatClient` | `uv sync` |
| `openai-compatible` | `OpenAIChatClient` | `uv sync` |
| `ollama` | `OllamaChatClient` | `uv sync` |
| `anthropic` | `AnthropicClient` | `uv sync --extra anthropic` |
| `foundry` | `FoundryChatClient` | `uv sync --extra foundry` |
| `foundry-local` | `FoundryLocalClient` | `uv sync --extra foundry-local` |
| `bedrock` | `BedrockChatClient` | `uv sync --extra bedrock` |

`openai-compatible` is the catch-all. It reaches OpenRouter, Groq, Cerebras,
Together, Fireworks, DeepSeek, xAI, LM Studio, vLLM and anything else that
speaks the OpenAI wire format — set `LLM_BASE_URL` and go.

Free tiers worth knowing about now that GitHub Models is gone: Google AI Studio,
Groq, Cerebras, OpenRouter and Mistral. Ollama and Foundry Local need no key at
all.

### Two rules the factory enforces

**No default model names.** Every provider requires an explicit `LLM_MODEL`.
Provider catalogues churn, and a baked-in default rots into an unexplained 404
months later.

**Every failure names the fix.** An unknown provider prints the supported list, a
missing variable is named along with what it wants, and a missing package prints
the `uv sync` command that installs it.

```text
Provider 'azure-openai' (Azure OpenAI) is missing required configuration.

Set the following in app/.env:
  LLM_API_KEY   an Azure OpenAI resource key
  LLM_BASE_URL  https://<your-resource>.openai.azure.com

Already set: LLM_MODEL
```

## Adding a provider

Add one `ProviderSpec` to the registry in [providers.py](providers.py) and a
fixture to `COMPLETE` in [tests/test_providers.py](tests/test_providers.py).
Nothing else changes — that is the point.

## Tests

```bash
uv run pytest
```

They run offline. A fixture blocks `socket.connect` outright, so "builds a client
without network access" is enforced rather than assumed, and another clears every
provider variable so a key in your own `.env` cannot change a result.

Providers whose package is not installed are skipped with the command that would
install them. To run the whole matrix:

```bash
uv sync --all-extras && uv run pytest
```

One provider cannot be built in tests: `foundry-local` starts the Foundry Local
runtime inside its constructor, so it needs that runtime on `PATH`. Its class
resolution is still covered; only the vendor's bootstrap is skipped.
