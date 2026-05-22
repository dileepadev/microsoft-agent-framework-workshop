# OpsAgent — FastAPI

REST API exposing OpsAgent — Module 9.

## Run the server

```bash
# From lab/app/web/fastapi/:
uvicorn server:app --reload
```

Open <http://localhost:8000/docs> for the interactive Swagger UI.

## Run the client

In a **separate** terminal (server must already be running):

```bash
# From lab/app/web/fastapi/:
python client.py
```

## Endpoints

| Method | Path | Description |
| --- | --- | --- |
| `GET` | `/api/health` | Health check |
| `POST` | `/api/chat` | Chat with OpsAgent (multi-turn) |
| `POST` | `/api/workflow` | Run the triage workflow |

## Multi-turn chat

Pass the same `session_id` across requests to keep conversation history and
user memory (Module 6 + 7) between calls.

```json
POST /api/chat
{
  "message": "My name is Alex. What can you help me with?",
  "session_id": "my-session"
}
```

## Triage workflow

```json
POST /api/workflow
{
  "query": "production server is down!"
}
```

Returns:

```json
{
  "severity": "CRITICAL",
  "query": "production server is down!",
  "response": "1. Verify connectivity… 2. Check logs…"
}
```
