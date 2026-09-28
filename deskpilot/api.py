"""FastAPI app: `POST /chat` (SSE trace + final reply), `GET /accounts/{id}`,
`POST /tickets`, `GET /tickets`.

Real Postgres/OpenAI wiring lives in `lifespan`, set on `app.state`. Route
handlers never touch `app.state` directly — they go through `Depends(get_stores)`
/ `Depends(get_chat_fn)` / `Depends(get_embed_fn)`, so `tests/test_api.py` can
override those with fakes and never trigger the real lifespan (no DB, no
OpenAI, per AGENTS.md's hermetic-suite rule) while still exercising the real
route/SSE wiring through `TestClient`.

`account_id` on `/chat` is this demo's stand-in for a logged-in session
(brief explicitly puts auth/multi-tenancy out of scope) — it's a structured
request field, not text parsed out of the chat message, which is what
actually matters for the prompt-injection defense: `deskpilot.agent`'s
`get_account`/`create_ticket` tools only ever see `AgentDeps.session_account_id`,
never anything from the model's tool-call arguments.
"""

import json
from collections.abc import Iterator
from contextlib import asynccontextmanager
from dataclasses import dataclass

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from deskpilot.accounts_store import AccountStore, InMemoryAccountStore
from deskpilot.agent import AgentDeps, AgentResult, ChatFn, run_turn_events
from deskpilot.config import database_url
from deskpilot.embeddings import embed_texts
from deskpilot.llm import chat_completion
from deskpilot.pg_ticket_store import PgTicketStore
from deskpilot.pgvector_store import PgVectorStore
from deskpilot.retrieval import EmbedFn, VectorStore
from deskpilot.seed.accounts import ACCOUNTS, SUBSCRIPTIONS
from deskpilot.tickets_store import Ticket, TicketStore
from eval.test_set import SESSION_ACCOUNT_ID


@asynccontextmanager
async def lifespan(app: FastAPI):  # pragma: no cover - real DB, exercised by running the app
    app.state.vector_store = PgVectorStore(database_url())
    app.state.account_store = InMemoryAccountStore(ACCOUNTS, SUBSCRIPTIONS)
    ticket_store = PgTicketStore(database_url())
    ticket_store.ensure_schema()
    app.state.ticket_store = ticket_store
    yield


app = FastAPI(title="DeskPilot", lifespan=lifespan)

# Local-only demo: the Next.js dev server (frontend/) runs on a different
# origin than the API. No auth in scope (build brief), so this stays a fixed
# localhost allowlist rather than a wildcard. 3001 covers `next dev` falling
# back when 3000 is already taken on the dev machine.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)


@dataclass(frozen=True)
class Stores:
    vector_store: VectorStore
    account_store: AccountStore
    ticket_store: TicketStore


def get_stores(request: Request) -> Stores:  # pragma: no cover - always overridden in tests
    return Stores(
        vector_store=request.app.state.vector_store,
        account_store=request.app.state.account_store,
        ticket_store=request.app.state.ticket_store,
    )


def get_chat_fn() -> ChatFn:  # pragma: no cover - always overridden in tests
    return chat_completion


def get_embed_fn() -> EmbedFn:  # pragma: no cover - always overridden in tests
    return embed_texts


class ChatRequest(BaseModel):
    query: str
    account_id: str = SESSION_ACCOUNT_ID


class TicketRequest(BaseModel):
    account_id: str
    subject: str
    summary: str
    priority: str


def _sse(event: str, data: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"


def _stream_chat(query: str, chat_fn: ChatFn, deps: AgentDeps) -> Iterator[str]:
    for event in run_turn_events(query, chat_fn, deps):
        if event.kind == "final":
            result: AgentResult = event.data
            yield _sse(
                "final",
                {
                    "reply": result.reply,
                    "tool_calls": result.tool_calls,
                    "cited_doc_ids": result.cited_doc_ids,
                    "ticket_id": result.ticket_id,
                },
            )
        else:
            yield _sse(event.kind, event.data)


def _ticket_dict(ticket: Ticket) -> dict:
    return {
        "id": ticket.id,
        "account_id": ticket.account_id,
        "subject": ticket.subject,
        "summary": ticket.summary,
        "priority": ticket.priority,
        "status": ticket.status,
    }


@app.post("/chat")
def chat(
    chat_request: ChatRequest,
    stores: Stores = Depends(get_stores),
    chat_fn: ChatFn = Depends(get_chat_fn),
    embed_fn: EmbedFn = Depends(get_embed_fn),
) -> StreamingResponse:
    deps = AgentDeps(
        vector_store=stores.vector_store,
        embed_fn=embed_fn,
        account_store=stores.account_store,
        ticket_store=stores.ticket_store,
        session_account_id=chat_request.account_id,
    )
    return StreamingResponse(
        _stream_chat(chat_request.query, chat_fn, deps), media_type="text/event-stream"
    )


@app.get("/accounts/{account_id}")
def get_account_endpoint(account_id: str, stores: Stores = Depends(get_stores)) -> dict:
    account = stores.account_store.get_account(account_id)
    if account is None:
        raise HTTPException(status_code=404, detail="account not found")
    return account


@app.post("/tickets")
def create_ticket_endpoint(
    ticket_request: TicketRequest, stores: Stores = Depends(get_stores)
) -> dict:
    ticket = stores.ticket_store.create_ticket(
        account_id=ticket_request.account_id,
        subject=ticket_request.subject,
        summary=ticket_request.summary,
        priority=ticket_request.priority,
    )
    return _ticket_dict(ticket)


@app.get("/tickets")
def list_tickets_endpoint(
    account_id: str | None = None, stores: Stores = Depends(get_stores)
) -> list[dict]:
    return [_ticket_dict(t) for t in stores.ticket_store.list_tickets(account_id=account_id)]
