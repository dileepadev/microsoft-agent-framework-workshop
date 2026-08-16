# Changelog

All notable changes to this project are documented in this file.

Changes are organized into the following categories:

- **Added:** New features or functionality introduced to the project.
- **Changed:** Modifications to existing functionality that do not add new features.
- **Fixed:** Bug fixes that resolve issues or correct unintended behavior.
- **Removed:** Features or components that have been removed from the project.

## [Unreleased]

## [2.0] - TBD

## [1.0] - 2026-08-15

The initial release (#1): a complete, working example of the workshop's one
idea — never run an agent inside the HTTP request — from the FastAPI backend
through to two deployed frontends and the teaching site that explains it.

### Added

- Initial public release of the *microsoft-agent-framework-workshop* repository.
- A 10-module, hands-on workshop that builds **OpsAgent**, an AI-powered operations and engineering assistant, from a first agent through to a hosted HTTP endpoint.
- GitHub Models-backed chat completions as the workshop's LLM provider, configured via a simple `.env` (`GITHUB_TOKEN`, `GITHUB_MODEL`).
- Tool calling with custom Python functions for Azure-oriented operational tasks (health checks, deployment helpers).
- Microsoft Learn live documentation access through an MCP server integration (`lab/app/shared/mcp.py`).
- Multi-turn conversations and persistent session memory.
- A triage workflow pipeline for orchestrated multi-agent runs (`lab/app/shared/workflow.py`).
- Four runnable chat interfaces over the same agent core: CLI, Chainlit, Streamlit, and FastAPI (with a demo client).
- An Azure Functions (Durable) hosting sample (`lab/app/hosting/`) that exposes the agent as a hosted HTTP endpoint.
- Module-by-module smoke-test/demo scripts (`lab/test_*.py`) for each core concept, runnable independently.
- The workshop website built with Astro and Tailwind CSS, published to GitHub Pages, covering all 10 modules plus an OpsAgent overview and a presentation deck page.
- QR code assets for sharing the live workshop URL, plus a custom 404 page.
- Repository scaffolding: MIT license, README with quick start and module table, and Astro docs site deployment via GitHub Actions.

<!-- e.g., -->
<!-- Unreleased -->
<!-- v2.0 -->
<!-- v1.1 -->
<!-- v1.0 -->
<!-- v0.0 -->

[Unreleased]: https://github.com/dileepadev/microsoft-agent-framework-workshop/compare/v1.0...HEAD
