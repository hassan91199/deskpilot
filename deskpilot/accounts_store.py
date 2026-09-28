"""Account + subscription lookup, keyed by the session's own account id only.

`get_account` (the tool, in `deskpilot.agent`) never accepts an account id
from the model — the id is bound into the agent loop via
`session_account_id` at construction time, which is what makes prompt
injection (eval query #10) structurally impossible rather than merely
discouraged in a prompt.
"""

from collections.abc import Sequence
from typing import Protocol


class AccountStore(Protocol):
    def get_account(self, account_id: str) -> dict | None: ...


class InMemoryAccountStore:
    """Seeded from `deskpilot.seed.accounts`. No DB needed — accounts and
    subscriptions are static demo data, not something the agent writes to."""

    def __init__(self, accounts: Sequence[dict], subscriptions: Sequence[dict]) -> None:
        subs_by_account = {sub["account_id"]: sub for sub in subscriptions}
        self._accounts = {
            account["id"]: {**account, **subs_by_account.get(account["id"], {})}
            for account in accounts
        }

    def get_account(self, account_id: str) -> dict | None:
        return self._accounts.get(account_id)
