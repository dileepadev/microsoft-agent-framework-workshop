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
| [mcp.py](mcp.py) | Microsoft Learn MCP server |
| [memory.py](memory.py) | Sessions, history and user memory |
| [workflow.py](workflow.py) | The triage workflow |
| [harness.py](harness.py) | OpsAgent as a Harness agent |
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

## Capabilities

Everything below is written once against the chat client the factory returns, so
none of it changes when the provider does.

**Tools** — three operational functions in [tools.py](tools.py). Two return canned
data and say so in their output, because an agent that reports an invented Azure
status as fact is worse than one with no tools.

**MCP** — the [Microsoft Learn server](mcp.py), hosted by Microsoft and needing no
key, so it works the same for everyone. It connects lazily, which is why an agent
holding MCP tools is used with `async with`.

**Sessions and memory** — [memory.py](memory.py). History is the transcript;
memory is a fact kept out of the transcript and re-injected each turn.

**Workflow** — [workflow.py](workflow.py) runs `triage_input → OpsAgent →
capture_output`. Severity classification is a keyword match, not a model call:
routing is the one decision here that has to be reproducible.

**Harness** — [harness.py](harness.py) is OpsAgent built with
`create_harness_agent`: planning and todos, context compaction, file memory, tool
approval and observability. Use it when the shape of the work is unknown; use the
workflow when you already know the steps.

### Persistence, precisely

Conversations are written as JSON under `app/.sessions/` (gitignored). Restart the
process, reload by session id, and the conversation is still there:

```bash
uv run python -m agent "my name is Sam, and our API is returning 429s"
uv run python -m agent "what did I say my name was?"
```

The second command is a new process that knows nothing except what is on disk.

That is the whole claim, and it is deliberately modest. It is not a database, it
does not survive an ephemeral host being redeployed, and it does not shard.
Swapping in Redis, Cosmos or Mem0 means changing the two factories in
[memory.py](memory.py) and nothing else.

> [!NOTE]
> `FileHistoryProvider`, `FileSessionStore` and the Harness file store are all
> marked **experimental** by the framework and warn on construction. They work,
> but the API may change. Pass `storage_dir=None` for in-memory instead.

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
