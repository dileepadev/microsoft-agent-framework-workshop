# 2. GitHub Models Connection

In this module, you'll set up access to **GitHub Models** and make your first AI API request using Python.

- [2. GitHub Models Connection](#2-github-models-connection)
  - [Learning Goals](#learning-goals)
  - [Introduction to GitHub Models](#introduction-to-github-models)
    - [Highlights](#highlights)
    - [API Endpoint](#api-endpoint)
  - [Step 1 - Generate a GitHub Access Token](#step-1---generate-a-github-access-token)
    - [Instructions](#instructions)
  - [Step 2 - Store the Token Securely](#step-2---store-the-token-securely)
  - [Step 3 - Create a Test Script](#step-3---create-a-test-script)
  - [Step 4 - Execute the Script](#step-4---execute-the-script)
    - [Example Output](#example-output)
  - [Code Walkthrough](#code-walkthrough)
    - [Creating the Client](#creating-the-client)
      - [What this does](#what-this-does)
    - [Sending a Chat Request](#sending-a-chat-request)
    - [Reading the Response](#reading-the-response)
  - [Recommended Models](#recommended-models)
  - [Suggested Project Layout](#suggested-project-layout)
  - [Completion Checklist](#completion-checklist)
  - [Next](#next)

## Learning Goals

After completing this section, you should be able to:

- Understand what GitHub Models is
- Generate a GitHub Personal Access Token (PAT)
- Configure environment variables securely
- Connect to an AI model using the OpenAI SDK
- Send and receive responses from a model

## Introduction to GitHub Models

GitHub provides a hosted AI inference service called **GitHub Models**, which gives developers access to several popular models through an OpenAI-compatible API.

### Highlights

| Capability | Description |
| --- | --- |
| AI Models | GPT-4o, GPT-4o-mini, o3-mini, and more |
| API Style | OpenAI-compatible |
| Authentication | GitHub Personal Access Token |
| Pricing | Includes a free usage tier |

### API Endpoint

```text
https://models.github.ai/inference
```

Because the API follows the OpenAI format, you can use the standard OpenAI Python library without major changes.

## Step 1 - Generate a GitHub Access Token

To use GitHub Models, you'll need a Personal Access Token.

### Instructions

1. Open GitHub token settings: `https://github.com/settings/tokens`
1. Select:

```text
Generate new token -> Generate new token (classic)
```

1. Configure the token:

| Setting | Suggested Value |
| --- | --- |
| Name | `microsoft-agent-framework-workshop-token` |
| Expiration | 30 days |
| Scopes | No additional scopes needed |

1. Click **Generate token**
1. Copy the token immediately and store it safely

> [!IMPORTANT]
> GitHub only shows the token once.

## Step 2 - Store the Token Securely

Create or update a `.env` file in your project root.

```env
GITHUB_TOKEN=your_token_here
GITHUB_MODEL=gpt-4o-mini
```

This keeps secrets outside your source code.

## Step 3 - Create a Test Script

Create a new Python file inside the current project root (`lab/`) for testing GitHub Models.

```bash
touch test_github_models_connection.py
```

Now add the following Python code.

```python
"""
Module 2 - Test GitHub Models Connection

Run:
    python test_github_models_connection.py
    or
    uv run test_github_models_connection.py
"""

import asyncio
import os

from dotenv import load_dotenv
from openai import AsyncOpenAI

load_dotenv()


async def main():
    """Send a simple request to GitHub Models."""

    print("🔌 Connecting to GitHub Models...")

    client = AsyncOpenAI(
        api_key=os.getenv("GITHUB_TOKEN"),
        base_url="https://models.github.ai/inference",
    )

    print("📨 Sending request...")

    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": "Reply with: Hello from GitHub Models!",
            }
        ],
    )

    message = response.choices[0].message.content

    print("\n💬 Model Response:", message)


if __name__ == "__main__":
    asyncio.run(main())
```

## Step 4 - Execute the Script

Run the test file:

```bash
python test_github_models_connection.py
# or
uv run test_github_models_connection.py
```

### Example Output

```text
🔌 Connecting to GitHub Models...
📨 Sending request...

💬 Model Response: Hello from GitHub Models!
```

If you receive a valid response, your setup is working correctly.

## Code Walkthrough

### Creating the Client

```python
client = AsyncOpenAI(
    api_key=os.getenv("GITHUB_TOKEN"),
    base_url="https://models.github.ai/inference",
)
```

#### What this does

| Parameter | Purpose |
| --- | --- |
| `api_key` | Uses your GitHub token |
| `base_url` | Redirects requests to GitHub Models |

### Sending a Chat Request

```python
response = await client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {
            "role": "user",
            "content": "Reply with: Hello from GitHub Models!",
        }
    ],
)
```

This sends a standard OpenAI-style chat request.

### Reading the Response

```python
message = response.choices[0].message.content
```

The generated text is stored inside the response object.

## Recommended Models

| Model | Best Use Case |
| --- | --- |
| `gpt-4o` | High-quality outputs |
| `gpt-4o-mini` | Fast and lightweight tasks |
| `o3-mini` | Reasoning-focused workflows |

For most workshop examples, `gpt-4o-mini` is a good default because it is fast and cost-efficient.

## Suggested Project Layout

```text
├── lab
│   ├── main.py
│   ├── pyproject.toml
│   ├── README.md
│   ├── requirements.txt
│   ├── test_github_models_connection.py
│   └── uv.lock
```

## Completion Checklist

| Task | Done |
| --- | --- |
| GitHub token created | ☐ |
| Token added to `.env` | ☐ |
| Test file created | ☐ |
| Script executed successfully | ☐ |
| AI response received | ☐ |

## Next

Continue to [3. Microsoft Agent Framework Agents](./3-microsoft-agent-framework-agents).
