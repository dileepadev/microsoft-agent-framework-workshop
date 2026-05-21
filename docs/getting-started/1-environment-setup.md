# 1. Environment Setup

Set up your local development environment to build your own AI agent from scratch. This workshop is designed for you to follow along and build a practical laboratory project.

- [1. Environment Setup](#1-environment-setup)
  - [Prerequisites Checklist](#prerequisites-checklist)
  - [Steps](#steps)
    - [1. Create Your Practical Lab Directory](#1-create-your-practical-lab-directory)
    - [2. Create and Activate Virtual Environment](#2-create-and-activate-virtual-environment)
    - [3. Install Core Dependencies](#3-install-core-dependencies)
    - [4. Create Environment File](#4-create-environment-file)
  - [Validation](#validation)
  - [Next](#next)

## Prerequisites Checklist

Before you begin, ensure you have:

- [ ] **Python 3.10+**: The core language for our agent logic.
- [ ] **uv**: An extremely fast Python package and environment manager.
- [ ] **VS Code** (Recommended): Our preferred code editor with excellent Python support.
- [ ] **Terminal Access**: macOS/Linux terminal or Windows PowerShell.
- [ ] **GitHub Account**: Required for accessing GitHub Models.
- [ ] **Git**: To version control your workspace (optional but recommended).

## Steps

### 1. Create Your Practical Lab Directory

Start by creating a dedicated folder for your workshop project. We are going to build **"OpsAgent"**, an intelligent cross-team operations agent that leverages the Microsoft Agent Framework to bridge tools and user interfaces.

> [!NOTE]
> This directory will serve as the root for all your project files and configurations.

```bash
# Initialize a new project
uv init lab --python 3.12
# or without a Python version (defaults to latest)
uv init lab

# Change into the project directory
cd lab
```

### 2. Create and Activate Virtual Environment

Use `uv` to manage your dependencies in an isolated environment.

```bash
# Create a virtual environment
uv venv

# Activate it (macOS / Linux)
source .venv/bin/activate

# Activate it (Windows)
.venv\Scripts\activate
```

### 3. Install Core Dependencies

We need specific libraries to build OpsAgent.

**What are we installing? and why we need them?**

- [agent-framework](https://pypi.org/project/agent-framework/): The Microsoft Agent Framework core for defining agent logic and workflows.
- [python-dotenv](https://pypi.org/project/python-dotenv/): To securely load configuration (like API tokens) from a `.env` file.
- [httpx](https://pypi.org/project/httpx/): A modern HTTP client for making asynchronous requests.
- [openai](https://pypi.org/project/openai/): The standard client for interacting with LLM providers (including GitHub Models).
- [chainlit](https://pypi.org/project/chainlit/): A beautiful framework to create a chat-based web interface instantly.
- [streamlit](https://pypi.org/project/streamlit/): Another popular framework for building interactive web apps with Python.

> [!IMPORTANT]
>
> - Make sure your virtual environment is activated before installing dependencies.
> - The installer will fail without the `--prerelease=allow` flag because `agent-framework` depends on a very specific beta version of `azure-search-documents` that is currently unavailable, so dependency resolution becomes impossible.

Install them using `uv`:

```bash
uv pip install agent-framework python-dotenv httpx openai chainlit streamlit --prerelease=allow

# or

uv add agent-framework python-dotenv httpx openai chainlit streamlit --prerelease=allow
```

> [!TIP]
> Alternatively, if you have a `requirements.txt` file, you can run `uv pip install -r requirements.txt`.  
>
> Below is an example `requirements.txt` content for reference:
>
> ```txt
> agent-framework
> python-dotenv
> httpx
> openai
> chainlit
> streamlit
> ```

### 4. Create Environment File

Create a `.env` file in the root of your `lab` directory:

```bash
touch .env
```

Add these lines to your `.env` file, replacing the placeholders with your actual GitHub token and desired model:

```env
GITHUB_TOKEN=your_github_token
GITHUB_MODEL=gpt-4o-mini
```

## Validation

Run the following to verify your environment is ready:

```bash
uv --version
python --version

uv run main.py

pip list | grep agent-framework
# or
uv pip list | grep agent-framework
```

## Next

Continue to [2. GitHub Models Connection](./2-github-models-connection.md).
