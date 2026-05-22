"""
Module 9 — OpsAgent FastAPI REST API

Exposes OpsAgent as a REST API so any HTTP client can use it.

  GET  /api/health    Health check
  POST /api/chat      Multi-turn chat (pass session_id to keep history)
  POST /api/workflow  Run the ops triage workflow

Features active on every request:
  Module 4 — Tool Calling:     Azure health check, deployment checklist, error diagnosis
  Module 5 — MCP Integration:  Microsoft Learn documentation
  Module 6 — Multi-Turn:       Sessions keyed by session_id
  Module 7 — Memory:           UserMemoryProvider per session
  Module 8 — Workflow:         POST /api/workflow

Run from lab/app/web/fastapi/:
    uvicorn server:app --reload

Open http://localhost:8000/docs for the interactive API documentation.
"""

import os
import sys
from contextlib import asynccontextmanager
from pathlib import Path

# ---------------------------------------------------------------------------
# Path setup — allows 'from app.shared.X import ...' when uvicorn runs here.
# ---------------------------------------------------------------------------
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent.parent.parent / ".env")

from fastapi import FastAPI
from pydantic import BaseModel

from app.shared.agent import (
    build_triage_workflow,
    classify_severity,
    create_chat_client,
    create_ops_agent,
)


def _get_required_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise ValueError("GITHUB_TOKEN and GITHUB_MODEL must be set in the .env file")
    return value


GITHUB_TOKEN = _get_required_env("GITHUB_TOKEN")
GITHUB_MODEL = _get_required_env("GITHUB_MODEL")


# ---------------------------------------------------------------------------
# In-memory session store
#
# Maps session_id (str) → AgentSession.
# A single agent instance is shared; each session holds its own history
# and memory state (UserMemoryProvider state is keyed by source_id inside
# the session, so sessions are fully isolated from each other).
# ---------------------------------------------------------------------------
_sessions: dict[str, object] = {}


# ---------------------------------------------------------------------------
# Lifespan — create / clean up the shared agent at server start / stop
# ---------------------------------------------------------------------------


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialise and clean up OpsAgent resources across the server lifetime."""
    client = create_chat_client(GITHUB_TOKEN, GITHUB_MODEL)
    agent = create_ops_agent(client)
    # async with keeps MCP tool connections properly managed.
    async with agent as managed_agent:
        app.state.agent = managed_agent
        app.state.client = client
        yield
    # Agent resources are released here when the server shuts down.


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------

app = FastAPI(
    title="OpsAgent API",
    description=(
        "REST API for OpsAgent — Module 9: Chat User Interface.\n\n"
        "Active features: Module 4 Tools · Module 5 MCP · "
        "Module 6 Multi-Turn · Module 7 Memory · Module 8 Workflow"
    ),
    version="1.0.0",
    lifespan=lifespan,
)


# ---------------------------------------------------------------------------
# Request / Response models
# ---------------------------------------------------------------------------


class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"

    model_config = {
        "json_schema_extra": {
            "example": {"message": "Check App Service health", "session_id": "user-1"}
        }
    }


class ChatResponse(BaseModel):
    response: str
    session_id: str


class WorkflowRequest(BaseModel):
    query: str

    model_config = {
        "json_schema_extra": {"example": {"query": "production server is down!"}}
    }


class WorkflowResponse(BaseModel):
    severity: str
    query: str
    response: str


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@app.get("/api/health", summary="Health check", tags=["utility"])
async def health():
    """Return server health status."""
    return {"status": "ok", "agent": "OpsAgent"}


@app.post(
    "/api/chat",
    response_model=ChatResponse,
    summary="Chat with OpsAgent (multi-turn)",
    tags=["chat"],
)
async def chat(request: ChatRequest):
    """
    Send a message to OpsAgent and receive a response.

    - Pass the same **session_id** across calls to maintain conversation history
      (Module 6) and user memory (Module 7).
    - OpsAgent will automatically call tools (Module 4) and consult Microsoft
      Learn via MCP (Module 5) when relevant.
    """
    agent = app.state.agent

    # Get or create the session for this session_id.
    if request.session_id not in _sessions:
        _sessions[request.session_id] = agent.create_session()
    session = _sessions[request.session_id]

    result = await agent.run(request.message, session=session)
    return ChatResponse(response=result.text, session_id=request.session_id)


@app.post(
    "/api/workflow",
    response_model=WorkflowResponse,
    summary="Run the ops triage workflow (Module 8)",
    tags=["workflow"],
)
async def run_workflow(request: WorkflowRequest):
    """
    Run the three-step triage workflow on the given ops query.

    Steps:  triage_input → OpsAgent → capture_output

    Returns the severity label (CRITICAL / HIGH / INFO) and OpsAgent's
    resolution steps.
    """
    client = app.state.client
    severity = classify_severity(request.query)

    workflow = build_triage_workflow(client)
    result = await workflow.run(request.query)
    outputs = result.get_outputs()

    return WorkflowResponse(
        severity=severity,
        query=request.query,
        response=outputs[0] if outputs else "(no output)",
    )
