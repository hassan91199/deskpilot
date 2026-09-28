"""Ticket creation. `InMemoryTicketStore` is the unit-test double (and what
the CLI/eval harness use by default); `deskpilot.pg_ticket_store.PgTicketStore`
is the real Postgres-backed implementation the FastAPI app uses, matching the
brief's "same Postgres holds accounts, subscriptions, tickets."

`account_id` always comes from `AgentDeps.session_account_id`, the same
session-bound pattern as `get_account` — never from free-text the user typed.
"""

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class Ticket:
    id: str
    account_id: str
    subject: str
    summary: str
    priority: str
    status: str = "open"


class TicketStore(Protocol):
    def create_ticket(
        self, account_id: str, subject: str, summary: str, priority: str
    ) -> Ticket: ...

    def list_tickets(self, account_id: str | None = None) -> list[Ticket]: ...


class InMemoryTicketStore:
    def __init__(self) -> None:
        self._tickets: list[Ticket] = []

    def create_ticket(self, account_id: str, subject: str, summary: str, priority: str) -> Ticket:
        ticket = Ticket(
            id=f"TCK-{1000 + len(self._tickets) + 1}",
            account_id=account_id,
            subject=subject,
            summary=summary,
            priority=priority,
        )
        self._tickets.append(ticket)
        return ticket

    def list_tickets(self, account_id: str | None = None) -> list[Ticket]:
        if account_id is None:
            return list(self._tickets)
        return [t for t in self._tickets if t.account_id == account_id]
