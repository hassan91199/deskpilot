"""Real Postgres implementation of `deskpilot.tickets_store.TicketStore`.

Deliberately untouched by the default unit-test gate (AGENTS.md: no network
calls, ever, in `tests/`) — same pattern as `deskpilot.pgvector_store`.
"""

import psycopg

from deskpilot.tickets_store import Ticket


class PgTicketStore:  # pragma: no cover
    def __init__(self, dsn: str) -> None:
        self._dsn = dsn

    def ensure_schema(self) -> None:
        with psycopg.connect(self._dsn) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS tickets (
                    seq SERIAL PRIMARY KEY,
                    account_id TEXT NOT NULL,
                    subject TEXT NOT NULL,
                    summary TEXT NOT NULL,
                    priority TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'open',
                    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
                )
                """
            )

    def create_ticket(self, account_id: str, subject: str, summary: str, priority: str) -> Ticket:
        with psycopg.connect(self._dsn) as conn:
            row = conn.execute(
                """
                INSERT INTO tickets (account_id, subject, summary, priority)
                VALUES (%s, %s, %s, %s)
                RETURNING seq, status
                """,
                (account_id, subject, summary, priority),
            ).fetchone()
        seq, status = row
        return Ticket(
            id=f"TCK-{1000 + seq}",
            account_id=account_id,
            subject=subject,
            summary=summary,
            priority=priority,
            status=status,
        )

    def list_tickets(self, account_id: str | None = None) -> list[Ticket]:
        query = "SELECT seq, account_id, subject, summary, priority, status FROM tickets"
        params: tuple = ()
        if account_id is not None:
            query += " WHERE account_id = %s"
            params = (account_id,)
        query += " ORDER BY seq"
        with psycopg.connect(self._dsn) as conn:
            rows = conn.execute(query, params).fetchall()
        return [
            Ticket(
                id=f"TCK-{1000 + row[0]}",
                account_id=row[1],
                subject=row[2],
                summary=row[3],
                priority=row[4],
                status=row[5],
            )
            for row in rows
        ]
