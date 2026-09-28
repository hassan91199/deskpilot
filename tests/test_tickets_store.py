import unittest

from deskpilot.tickets_store import InMemoryTicketStore


class InMemoryTicketStoreTests(unittest.TestCase):
    def test_create_ticket_assigns_incrementing_ids(self):
        store = InMemoryTicketStore()

        first = store.create_ticket("acct-1", "Double charge", "Charged twice this month", "high")
        second = store.create_ticket("acct-1", "Cancel plan", "Wants to cancel", "normal")

        self.assertEqual(first.id, "TCK-1001")
        self.assertEqual(second.id, "TCK-1002")
        self.assertEqual(first.status, "open")

    def test_list_tickets_returns_created_tickets(self):
        store = InMemoryTicketStore()
        store.create_ticket("acct-1", "Subject", "Summary", "low")

        tickets = store.list_tickets()

        self.assertEqual(len(tickets), 1)
        self.assertEqual(tickets[0].subject, "Subject")

    def test_list_tickets_filters_by_account_id(self):
        store = InMemoryTicketStore()
        store.create_ticket("acct-1", "Subject A", "Summary A", "low")
        store.create_ticket("acct-2", "Subject B", "Summary B", "low")

        tickets = store.list_tickets(account_id="acct-1")

        self.assertEqual([t.subject for t in tickets], ["Subject A"])


if __name__ == "__main__":
    unittest.main()
