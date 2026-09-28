"""In-memory ticket creation for the CLI and eval agent loop.

A Postgres-backed store (matching the brief's "same Postgres holds accounts,
subscriptions, tickets") lands with the FastAPI endpoints in DP-4, once
`GET /tickets` needs a store that outlives a single process. Until then this
is the only implementation `deskpilot.agent.run_turn` talks to.
"""

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class Ticket:
    id: str
    subject: str
    summary: str
    priority: str
    status: str = "open"


class TicketStore(Protocol):
    def create_ticket(self, subject: str, summary: str, priority: str) -> Ticket: ...


class InMemoryTicketStore:
    def __init__(self) -> None:
        self._tickets: list[Ticket] = []

    def create_ticket(self, subject: str, summary: str, priority: str) -> Ticket:
        ticket = Ticket(
            id=f"TCK-{1000 + len(self._tickets) + 1}",
            subject=subject,
            summary=summary,
            priority=priority,
        )
        self._tickets.append(ticket)
        return ticket

    def list_tickets(self) -> list[Ticket]:
        return list(self._tickets)
