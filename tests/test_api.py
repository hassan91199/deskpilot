import unittest

from fastapi.testclient import TestClient

from deskpilot.accounts_store import InMemoryAccountStore
from deskpilot.agent import AssistantMessage, ToolCall
from deskpilot.api import Stores, app, get_chat_fn, get_embed_fn, get_stores
from deskpilot.retrieval import Chunk, InMemoryVectorStore
from deskpilot.tickets_store import InMemoryTicketStore

ACCOUNTS = [{"id": "acct-1", "name": "Aeon Robotics", "email": "ops@aeon.example"}]
SUBSCRIPTIONS = [
    {"account_id": "acct-1", "plan": "pro", "seats_used": 8, "seat_limit": 10},
]


class ScriptedChatFn:
    def __init__(self, responses):
        self._responses = list(responses)

    def __call__(self, messages, tool_schemas):
        return self._responses.pop(0)


def _parse_sse(body: str) -> list[tuple[str, str]]:
    events = []
    for block in body.strip().split("\n\n"):
        lines = block.splitlines()
        event = next(line.removeprefix("event: ") for line in lines if line.startswith("event: "))
        data = next(line.removeprefix("data: ") for line in lines if line.startswith("data: "))
        events.append((event, data))
    return events


class ApiTestCase(unittest.TestCase):
    def setUp(self):
        self.vector_store = InMemoryVectorStore()
        self.vector_store.upsert(
            [
                Chunk(
                    id="rotating-an-api-key",
                    doc_id="rotating-an-api-key",
                    doc_title="Rotating an API Key",
                    text="...",
                )
            ],
            [[1.0, 0.0]],
        )
        self.account_store = InMemoryAccountStore(ACCOUNTS, SUBSCRIPTIONS)
        self.ticket_store = InMemoryTicketStore()

        app.dependency_overrides[get_stores] = lambda: Stores(
            vector_store=self.vector_store,
            account_store=self.account_store,
            ticket_store=self.ticket_store,
        )
        app.dependency_overrides[get_embed_fn] = lambda: lambda texts: [[1.0, 0.0] for _ in texts]
        self.client = TestClient(app)

    def tearDown(self):
        app.dependency_overrides.clear()

    def _use_chat_fn(self, responses):
        app.dependency_overrides[get_chat_fn] = lambda: ScriptedChatFn(responses)


class ChatEndpointTests(ApiTestCase):
    def test_streams_tool_call_tool_result_and_final_events(self):
        self._use_chat_fn(
            [
                AssistantMessage(
                    content=None,
                    tool_calls=[
                        ToolCall(id="c1", name="search_docs", arguments={"query": "rotate key"})
                    ],
                ),
                AssistantMessage(content="Here's how to rotate your key.", tool_calls=[]),
            ]
        )

        response = self.client.post(
            "/chat", json={"query": "How do I rotate an API key?", "account_id": "acct-1"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["content-type"], "text/event-stream; charset=utf-8")
        events = _parse_sse(response.text)
        self.assertEqual([kind for kind, _ in events], ["tool_call", "tool_result", "final"])
        self.assertIn("Sources: Rotating an API Key", events[2][1])

    def test_defaults_account_id_when_omitted(self):
        self._use_chat_fn([AssistantMessage(content="Declined.", tool_calls=[])])

        response = self.client.post("/chat", json={"query": "Who won the football match?"})

        events = _parse_sse(response.text)
        self.assertEqual(events[0][0], "final")
        self.assertIn("Declined.", events[0][1])


class AccountsEndpointTests(ApiTestCase):
    def test_returns_known_account(self):
        response = self.client.get("/accounts/acct-1")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["name"], "Aeon Robotics")

    def test_404s_for_unknown_account(self):
        response = self.client.get("/accounts/acct-does-not-exist")

        self.assertEqual(response.status_code, 404)


class TicketsEndpointTests(ApiTestCase):
    def test_create_then_list_round_trips(self):
        create_response = self.client.post(
            "/tickets",
            json={
                "account_id": "acct-1",
                "subject": "Double charge",
                "summary": "Charged twice",
                "priority": "high",
            },
        )
        self.assertEqual(create_response.status_code, 200)
        self.assertEqual(create_response.json()["id"], "TCK-1001")

        list_response = self.client.get("/tickets")
        self.assertEqual(len(list_response.json()), 1)
        self.assertEqual(list_response.json()[0]["subject"], "Double charge")

    def test_list_filters_by_account_id(self):
        self.ticket_store.create_ticket("acct-1", "A", "A", "low")
        self.ticket_store.create_ticket("acct-2", "B", "B", "low")

        response = self.client.get("/tickets", params={"account_id": "acct-2"})

        self.assertEqual([t["subject"] for t in response.json()], ["B"])


if __name__ == "__main__":
    unittest.main()
