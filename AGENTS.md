# DeskPilot agent conventions

Operating rules for anyone (or any agent — Claude Code, OpenCode, Codex, or
otherwise) working in this repo. This file is the single source of truth and
is deliberately kept agent-agnostic: don't split conventions off into a
tool-specific file (e.g. `CLAUDE.md`) that only one tool reads, since that
leaves every other agent blind to it. If a tool needs its own short pointer
file to discover this one (Claude Code looks for `CLAUDE.md`), that pointer
file must contain nothing but a link back here — no conventions live in it.

Build brief (source of truth for scope, architecture and behaviour rules):
`.docs/ai_support_agent_build_brief.md` (local, not committed — recreate from
`personal-docs/.docs/ai_support_agent_build_brief.md` if it's missing).

## Testing: test-first is the default workflow

For every bug fix or feature, work in this order:

1. **RED** — write the test that captures the new behavior or reproduces the
   bug. Run it and confirm it fails for the expected reason.
2. **GREEN** — implement the smallest change that makes the full suite pass.
3. **REFACTOR** — clean up with the suite green, re-run `scripts/test.sh`
   before committing.

Never commit implementation without the test that pins it. Never weaken an
assertion, a coverage floor, or a lint rule to make a change fit.

## Test layers (what goes where)

| Layer | Location | Runs via | Cost per run | What belongs here |
| --- | --- | --- | --- | --- |
| Unit | `tests/test_*.py` | in-process, fakes | free | Seed data integrity, retrieval/chunking logic, individual tool functions, agent-loop branching (LLM faked) |
| Integration | `tests/test_agent.py`, `tests/test_api.py` | FastAPI `TestClient`, LLM + DB faked | free | Full turn: tool routing, round cap, SSE stream shape, escalation rules |
| Frontend | `frontend/**/*.test.{ts,tsx}` | Vitest + React Testing Library, fetch mocked | free | `lib/api.ts` SSE parsing, `ChatWindow`/`TracePanel`/`AccountSwitcher` rendering and interaction |
| Container | `docker run --rm deskpilot test` | same suite inside the image | free | Env parity: deps, entrypoint, permissions |
| Eval (opt-in) | `eval/run_eval.py` | real OpenAI + seeded Postgres | ~cents/run | The 10 locked queries (`eval/test_set.py`): pass rate, latency, cost. Never part of the default suite. |
| Real smoke | manual, or CI on-demand | live APIs, deployed service | small $ | Pre-recording sanity check before the walkthrough |

Rules that keep the default suite hermetic:

- **No network calls in tests, ever.** The OpenAI client is always patched
  with a fake. The DB layer is written behind a small repository interface
  so unit/integration tests can use an in-memory fake instead of a real
  Postgres — no test container in the default gate.
- Tests never depend on the host's `.env` — they patch env vars explicitly.
- Real OpenAI + real Postgres are only ever touched by explicitly-invoked
  entrypoints — `eval/run_eval.py`, `deskpilot/cli.py`, `deskpilot/ingest.py`,
  and the FastAPI app's `lifespan`/`get_stores`/`get_chat_fn`/`get_embed_fn`
  (`deskpilot/api.py`) — never by `scripts/test.sh` or CI's default job.
  `tests/test_api.py` exercises the real route/SSE wiring through
  `TestClient`, but overrides every one of those dependency functions with a
  fake, so the real lifespan never runs during tests.
- A tiny in-memory fixture (a handful of docs/accounts) is enough for unit
  tests; the full seed set (`deskpilot/seed/`) is what `eval/run_eval.py`
  and local dev load into real Postgres.

## Commands

```sh
.venv/bin/python scripts/test.sh   # lint + format + full suite under coverage
docker run --rm deskpilot          # same gate inside the container
python -m eval.run_eval            # opt-in: the 10 locked queries against real APIs
python -m deskpilot.cli            # opt-in: interactive agent loop against real APIs
.venv/bin/uvicorn deskpilot.api:app --reload   # opt-in: the FastAPI app, real DB/OpenAI
.venv/bin/ruff format deskpilot eval tests scripts   # format
cd frontend && npm test            # frontend: Vitest component/unit suite
cd frontend && npx tsc --noEmit && npm run lint   # frontend: type-check + eslint
```

Coverage floor is set in `pyproject.toml` (`[tool.coverage.report] fail_under`).
Raise the floor when coverage grows; never lower it to land a change.

## Behaviour rules (from the build brief — enforce these in code and tests)

- Answer only from retrieved chunks. If retrieval similarity is under
  threshold, say so and offer a ticket. No guessing.
- The account tool takes its account id from the session, never from the
  user's message — this is the prompt-injection defense (test query #10).
- Ticket creation always echoes the ticket id back to the user.
- Refunds, cancellations and anything outside the docs go to a ticket. The
  agent never promises an outcome.
- Every reply that used docs cites the source doc titles.
- Cap tool-calling at 4 rounds per turn.

## Style

- `ruff` with `E,F,W,I` at line length 100; `ruff format` is the formatter.
  Both are checked in the same gate as the tests.
- Python 3.12, stdlib `unittest` (not pytest) — one class per concern,
  `patch` with explicit targets, matching ClipForge's style in this same
  workspace.
- Comments explain *why*; code and test names explain *what*.
- Dependencies: runtime pins in `requirements.txt`, dev tools in
  `requirements-dev.txt`. Both installed in the Docker image so the container
  gate matches local.

## Git remote and pushing

Remote: `origin` = `https://github.com/hassan91199/deskpilot.git`. This
machine's `gh` CLI is logged into a different account by default, so pushes
here must go through the `hassan-personal` identity wrapper, not a bare
`git push`:

```sh
as-hassan-personal git push
as-hassan-personal git push -u origin <branch>   # first push of a new branch
```

The repo's local git config already scopes a credential helper to
`https://github.com/hassan91199` for this. Full mechanism (why the wrapper
is needed, how to verify it, troubleshooting) is documented in
`personal-docs/.docs/git_multi_account_auth_setup.txt` — read that before
changing anything here, don't just copy this snippet elsewhere.

## ClickUp task workflow

This is a portfolio-demo project. Any ClickUp task tracking it must link to
`strategies/demo_deployment_strategy.md` (in `personal-docs`) — the policy on
whether and how a finished demo gets shown publicly, and who is responsible
for any actual deploy or teardown.

The original tracking task lives at https://app.clickup.com/t/z8tj1ha4ce.

Tasks live in **proj-deskpilot** (`list_id: 1100390000073864`), in the
"Projects" folder (`folder_id: 90186953295`, space "Hassan's Space"
`90184111502`) alongside proj-clipforge `1100390000016137`, proj-swiftreels
`901807349061`, proj-cloakmotion `1100390000013942`, proj-nepo
`1100390000052427`, proj-markit `1100390000052782`. This list initially
existed under the same name with an unrelated "NewsPoet" description (a
naming collision from elsewhere) — confirmed with the user on 2026-09-28 and
repurposed for DeskPilot; its history before that date is not this
project's.

The full DP-1..DP-13 task breakdown (mirroring the build brief's build
order + "after it ships" steps) was created in this list on 2026-09-28.

### Naming and numbering

- Every task is titled `DP-<N> <short title>`, where `<N>` is one more than
  the highest existing DP number in the workspace.
- To find the current highest `<N>`: `clickup_search` with
  `keywords: "DP-"`, `filters.asset_types: ["task"]`. Results are **not**
  sorted numerically and are paginated — follow every `next_cursor` until it
  comes back `null`, then take the max `N` parsed from all titles seen.

### Status

- Leave `status` unset on creation (list default applies) unless the user
  says where the task should start.
- Verify the list's actual status names with `clickup_get_list` once the
  list exists, rather than assuming they match another project's.

### Description and priority

- Write `markdown_description` with a `## Problem`/`## Scope` structure
  when there's enough context — cite concrete evidence (error messages,
  file paths) for the problem, and list concrete files/dirs in scope.
- If the task is unclear enough to need target decisions the user hasn't
  given yet, add an `## Open questions` section rather than guessing —
  create the task anyway so it's tracked, but don't invent specifics.
- Default `priority` to `normal` unless told otherwise.

### Git branches

- Never commit directly to `main`. All work happens on a branch; `main`
  only ever changes by merging a branch into it (`git merge --no-ff`, then
  push `main`). Never force-push.
- If the work is tracked by a ClickUp ticket, the branch is named `dp-<N>`
  matching that ticket's **actual** number — never invent the "next
  sequential number" as a branch name when no ticket backs it.
- If told **not** to file a ClickUp task for a piece of work (e.g. a quick
  bug fix):
  - If a branch for the current task/conversation is already checked out
    and in progress, do the work there.
  - Otherwise, create a new branch, but name it for what the work actually
    is (not an invented `dp-<N>`), e.g. `fix-retrieval-threshold`.
  - Either way, still merge into `main` the normal way when done.
