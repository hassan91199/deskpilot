"""Seed accounts and subscriptions for the fictional Acme Cloud SaaS.

Plain data (no DB dependency) so tests can validate it against
`deskpilot.seed.docs` and `eval.test_set` without a database. Seat limits
here must match the numbers in the "Seat Limits by Plan" doc; renewal dates
and plans here are what the account-tool eval queries assert against.
"""

ACCOUNTS = [
    {
        "id": "acct-1",
        "name": "Aeon Robotics",
        "email": "ops@aeonrobotics.example",
    },
    {
        "id": "acct-2",
        "name": "Blue Harbor Logistics",
        "email": "billing@blueharborlogistics.example",
    },
    {
        "id": "acct-3",
        "name": "Cascade Analytics",
        "email": "admin@cascadeanalytics.example",
    },
]

# seat_limit mirrors the "Seat Limits by Plan" doc (Free 1, Starter 5, Pro
# 10, Enterprise 100) — kept explicit per-row rather than derived, so a
# seed-data test can catch the two drifting apart.
SUBSCRIPTIONS = [
    {
        "account_id": "acct-1",
        "plan": "pro",
        "seats_used": 8,
        "seat_limit": 10,
        "billing_cycle": "monthly",
        "renewal_date": "2026-11-15",
        "status": "active",
    },
    {
        "account_id": "acct-2",
        "plan": "starter",
        "seats_used": 3,
        "seat_limit": 5,
        "billing_cycle": "annual",
        "renewal_date": "2026-10-01",
        "status": "active",
    },
    {
        "account_id": "acct-3",
        "plan": "enterprise",
        "seats_used": 40,
        "seat_limit": 100,
        "billing_cycle": "annual",
        "renewal_date": "2027-01-20",
        "status": "active",
    },
]
