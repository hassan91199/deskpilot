import unittest

from deskpilot.accounts_store import InMemoryAccountStore

ACCOUNTS = [{"id": "acct-1", "name": "Aeon Robotics", "email": "ops@aeon.example"}]
SUBSCRIPTIONS = [
    {"account_id": "acct-1", "plan": "pro", "seats_used": 8, "seat_limit": 10},
]


class InMemoryAccountStoreTests(unittest.TestCase):
    def test_merges_account_and_subscription_fields(self):
        store = InMemoryAccountStore(ACCOUNTS, SUBSCRIPTIONS)

        account = store.get_account("acct-1")

        self.assertEqual(account["name"], "Aeon Robotics")
        self.assertEqual(account["plan"], "pro")
        self.assertEqual(account["seats_used"], 8)

    def test_unknown_account_returns_none(self):
        store = InMemoryAccountStore(ACCOUNTS, SUBSCRIPTIONS)

        self.assertIsNone(store.get_account("acct-does-not-exist"))


if __name__ == "__main__":
    unittest.main()
