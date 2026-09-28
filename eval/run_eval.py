"""Opt-in eval harness: the 10 locked queries against real OpenAI + real
Postgres. Never part of the default suite (AGENTS.md) — run explicitly:

    .venv/bin/python -m eval.run_eval

Reports pass rate and median/p95 latency, per the build brief's "Done means".
Per-conversation cost isn't reported yet: it needs token-usage plumbing
through `embed_texts`/`chat_completion` that doesn't exist yet, and the
brief says not to estimate it — fast-follow once that's wired up.
"""

import statistics
import time

from deskpilot.accounts_store import InMemoryAccountStore
from deskpilot.agent import AgentDeps, run_turn
from deskpilot.config import database_url
from deskpilot.embeddings import embed_texts
from deskpilot.llm import chat_completion
from deskpilot.pgvector_store import PgVectorStore
from deskpilot.seed.accounts import ACCOUNTS, SUBSCRIPTIONS
from deskpilot.tickets_store import InMemoryTicketStore
from eval.test_set import SESSION_ACCOUNT_ID, TEST_SET


def _grade(case: dict, result) -> bool:
    calls_ok = set(case["expected_tool_calls"]) <= set(result.tool_calls)
    cited_ok = set(case["expected_cited_doc_ids"]) <= set(result.cited_doc_ids)
    ticket_ok = case["expect_ticket"] == (result.ticket_id is not None)
    refusal_ok = case["expect_refusal"] == (len(result.tool_calls) == 0)
    return calls_ok and cited_ok and ticket_ok and refusal_ok


def main() -> None:  # pragma: no cover
    vector_store = PgVectorStore(database_url())
    account_store = InMemoryAccountStore(ACCOUNTS, SUBSCRIPTIONS)

    rows = []
    latencies = []
    passed = 0
    for case in TEST_SET:
        deps = AgentDeps(
            vector_store=vector_store,
            embed_fn=embed_texts,
            account_store=account_store,
            ticket_store=InMemoryTicketStore(),
            session_account_id=SESSION_ACCOUNT_ID,
        )
        start = time.monotonic()
        result = run_turn(case["query"], chat_completion, deps)
        elapsed = time.monotonic() - start
        latencies.append(elapsed)

        ok = _grade(case, result)
        passed += int(ok)
        rows.append((case["id"], case["category"], "PASS" if ok else "FAIL", elapsed))

    print(f"{'#':<3} {'category':<18} {'result':<6} {'latency'}")
    for case_id, category, verdict, elapsed in rows:
        print(f"{case_id:<3} {category:<18} {verdict:<6} {elapsed:.2f}s")

    median = statistics.median(latencies)
    p95 = statistics.quantiles(latencies, n=20)[18] if len(latencies) >= 2 else latencies[0]
    print(f"\n{passed}/{len(TEST_SET)} passed. median={median:.2f}s p95={p95:.2f}s")


if __name__ == "__main__":
    main()
