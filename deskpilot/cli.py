"""Interactive CLI for the DeskPilot agent loop — real OpenAI, real Postgres,
seeded in-memory accounts/tickets, session bound to `SESSION_ACCOUNT_ID`.

    .venv/bin/python -m deskpilot.cli
"""

from deskpilot.accounts_store import InMemoryAccountStore
from deskpilot.agent import AgentDeps, run_turn
from deskpilot.config import database_url
from deskpilot.embeddings import embed_texts
from deskpilot.llm import chat_completion
from deskpilot.pgvector_store import PgVectorStore
from deskpilot.seed.accounts import ACCOUNTS, SUBSCRIPTIONS
from deskpilot.tickets_store import InMemoryTicketStore
from eval.test_set import SESSION_ACCOUNT_ID


def main() -> None:  # pragma: no cover
    deps = AgentDeps(
        vector_store=PgVectorStore(database_url()),
        embed_fn=embed_texts,
        account_store=InMemoryAccountStore(ACCOUNTS, SUBSCRIPTIONS),
        ticket_store=InMemoryTicketStore(),
        session_account_id=SESSION_ACCOUNT_ID,
    )

    print(f"DeskPilot CLI — session account {SESSION_ACCOUNT_ID}. Ctrl-D to quit.")
    while True:
        try:
            query = input("\nyou> ").strip()
        except EOFError:
            print()
            break
        if not query:
            continue
        result = run_turn(query, chat_completion, deps)
        print(f"\nagent> {result.reply}")


if __name__ == "__main__":
    main()
