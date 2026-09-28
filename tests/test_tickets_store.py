import unittest

from deskpilot.tickets_store import InMemoryTicketStore


class InMemoryTicketStoreTests(unittest.TestCase):
    def test_create_ticket_assigns_incrementing_ids(self):
        store = InMemoryTicketStore()

        first = store.create_ticket("Double charge", "Charged twice this month", "high")
        second = store.create_ticket("Cancel plan", "Wants to cancel", "normal")

        self.assertEqual(first.id, "TCK-1001")
        self.assertEqual(second.id, "TCK-1002")
        self.assertEqual(first.status, "open")

    def test_list_tickets_returns_created_tickets(self):
        store = InMemoryTicketStore()
        store.create_ticket("Subject", "Summary", "low")

        tickets = store.list_tickets()

        self.assertEqual(len(tickets), 1)
        self.assertEqual(tickets[0].subject, "Subject")


if __name__ == "__main__":
    unittest.main()
