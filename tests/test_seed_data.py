import unittest

from deskpilot.seed.accounts import ACCOUNTS, SUBSCRIPTIONS
from deskpilot.seed.docs import DOCS
from eval.test_set import SESSION_ACCOUNT_ID, TEST_SET

# Mirrors the "Seat Limits by Plan" doc body: Free 1, Starter 5, Pro 10,
# Enterprise 100. Kept here as an independent expectation so a change to
# either docs.py or accounts.py that breaks the pairing fails loudly.
EXPECTED_SEAT_LIMIT_BY_PLAN = {"free": 1, "starter": 5, "pro": 10, "enterprise": 100}

EXPECTED_CATEGORY_COUNTS = {
    "faq": 3,
    "faq_multi_chunk": 1,
    "account_tool": 2,
    "tool_plus_rag": 1,
    "escalation": 1,
    "out_of_scope": 1,
    "prompt_injection": 1,
}


class DocsSeedTests(unittest.TestCase):
    def test_doc_count_in_brief_range(self):
        self.assertGreaterEqual(len(DOCS), 20)
        self.assertLessEqual(len(DOCS), 30)

    def test_doc_ids_are_unique(self):
        ids = [doc["id"] for doc in DOCS]
        self.assertEqual(len(ids), len(set(ids)))

    def test_every_doc_has_required_fields(self):
        for doc in DOCS:
            for field in ("id", "title", "category", "body"):
                self.assertIn(field, doc)
                self.assertTrue(doc[field], f"{field} empty on doc {doc.get('id')}")

    def test_categories_match_brief_topics(self):
        allowed = {
            "plans",
            "billing",
            "limits",
            "api_keys",
            "sso",
            "refunds",
            "account_management",
        }
        categories = {doc["category"] for doc in DOCS}
        self.assertTrue(categories.issubset(allowed), categories - allowed)


class AccountsSeedTests(unittest.TestCase):
    def test_account_ids_are_unique(self):
        ids = [acct["id"] for acct in ACCOUNTS]
        self.assertEqual(len(ids), len(set(ids)))

    def test_every_account_has_exactly_one_subscription(self):
        account_ids = {acct["id"] for acct in ACCOUNTS}
        sub_account_ids = [sub["account_id"] for sub in SUBSCRIPTIONS]
        self.assertEqual(set(sub_account_ids), account_ids)
        self.assertEqual(len(sub_account_ids), len(set(sub_account_ids)))

    def test_seat_limits_match_seat_limits_by_plan_doc(self):
        for sub in SUBSCRIPTIONS:
            expected = EXPECTED_SEAT_LIMIT_BY_PLAN[sub["plan"]]
            self.assertEqual(
                sub["seat_limit"],
                expected,
                f"{sub['account_id']} ({sub['plan']}) seat_limit drifted from the doc",
            )

    def test_acct_1_seat_math_for_query_7(self):
        acct_1 = next(s for s in SUBSCRIPTIONS if s["account_id"] == "acct-1")
        self.assertGreater(acct_1["seats_used"] + 5, acct_1["seat_limit"])


class EvalTestSetTests(unittest.TestCase):
    def test_exactly_ten_queries_with_unique_ids_1_to_10(self):
        ids = [q["id"] for q in TEST_SET]
        self.assertEqual(sorted(ids), list(range(1, 11)))

    def test_category_mix_matches_brief(self):
        counts = {}
        for q in TEST_SET:
            counts[q["category"]] = counts.get(q["category"], 0) + 1
        self.assertEqual(counts, EXPECTED_CATEGORY_COUNTS)

    def test_cited_doc_ids_exist_in_docs(self):
        doc_ids = {doc["id"] for doc in DOCS}
        for q in TEST_SET:
            for cited in q["expected_cited_doc_ids"]:
                self.assertIn(cited, doc_ids, f"query {q['id']} cites unknown doc {cited}")

    def test_session_account_exists_and_is_not_the_injection_target(self):
        account_ids = {acct["id"] for acct in ACCOUNTS}
        self.assertIn(SESSION_ACCOUNT_ID, account_ids)

        injection_query = next(q for q in TEST_SET if q["category"] == "prompt_injection")
        self.assertIn("account 2", injection_query["query"])
        self.assertNotEqual(SESSION_ACCOUNT_ID, "acct-2")
        self.assertIn("acct-2", account_ids)

    def test_queries_expecting_a_ticket_also_have_no_cited_docs(self):
        # Ticket-worthy turns (refunds etc.) must not fabricate a citation
        # for something the docs explicitly say the agent can't promise.
        for q in TEST_SET:
            if q["expect_ticket"]:
                self.assertEqual(q["expected_cited_doc_ids"], [])


if __name__ == "__main__":
    unittest.main()
