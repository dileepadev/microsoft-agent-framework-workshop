"""
Module 9 — OpsAgent API Client

Demonstrates calling the OpsAgent FastAPI REST API using httpx.

Start the server first:
    uvicorn server:app --reload    (from lab/app/web/fastapi/)

Then run this script:
    python client.py               (from lab/app/web/fastapi/)
"""

import httpx

BASE_URL = "http://localhost:8000"

# All requests in this demo share the same session_id so conversation history
# and memory (user name) are preserved across calls — demonstrating Module 6 + 7.
SESSION_ID = "workshop-demo"


# ---------------------------------------------------------------------------
# API helpers
# ---------------------------------------------------------------------------


def health_check() -> None:
    """GET /api/health — confirm the server is running."""
    resp = httpx.get(f"{BASE_URL}/api/health", timeout=10.0)
    resp.raise_for_status()
    print(f"✅ Health: {resp.json()}\n")


def chat(message: str, session_id: str = SESSION_ID) -> str:
    """POST /api/chat — send a message and return OpsAgent's response text."""
    resp = httpx.post(
        f"{BASE_URL}/api/chat",
        json={"message": message, "session_id": session_id},
        timeout=60.0,
    )
    resp.raise_for_status()
    return resp.json()["response"]


def run_workflow(query: str) -> dict:
    """POST /api/workflow — run the triage pipeline and return the result dict."""
    resp = httpx.post(
        f"{BASE_URL}/api/workflow",
        json={"query": query},
        timeout=60.0,
    )
    resp.raise_for_status()
    return resp.json()


# ---------------------------------------------------------------------------
# Demo sequence
# ---------------------------------------------------------------------------


def main() -> None:
    print("=" * 62)
    print("  OpsAgent API Client  —  Module 9")
    print("=" * 62 + "\n")

    # 1. Health check
    health_check()

    # 2. Multi-turn chat  (Modules 4, 5, 6, 7)
    #    All three calls share SESSION_ID, so history and memory persist.
    print("── Multi-turn Chat ─────────────────────────────────────────")

    q1 = "My name is Alex. What can you help me with?"
    print(f"👤 You:       {q1}")
    print(f"💬 OpsAgent: {chat(q1)}\n")

    q2 = "Check the health of App Service in East US."
    print(f"👤 You:       {q2}")
    print(f"💬 OpsAgent: {chat(q2)}\n")

    q3 = "What is my name?"  # tests Module 7 — memory recall
    print(f"👤 You:       {q3}")
    print(f"💬 OpsAgent: {chat(q3)}\n")

    # 3. Workflow  (Module 8)
    print("── Triage Workflow ─────────────────────────────────────────")

    for query in (
        "production server is down!",
        "CPU spike at 95%",
        "deploy checklist for AKS",
    ):
        result = run_workflow(query)
        print(f"🔍 Query:    {result['query']}")
        print(f"   Severity: {result['severity']}")
        print(f"   Response: {result['response'][:120]}…\n")


if __name__ == "__main__":
    main()
