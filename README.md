# DeskPilot

AI customer support agent (RAG + account actions) for a fictional SaaS,
"Acme Cloud." Work in progress — see `AGENTS.md` for how this repo is built
(test-first) and `.docs/ai_support_agent_build_brief.md` for full scope.

**Status:** seed data, retrieval (pgvector), the tool-calling agent loop,
the FastAPI backend (`POST /chat` SSE, accounts, tickets), a Next.js chat UI
with a trace panel (`frontend/`), the backend/frontend test suites, a
Dockerfile, and CI (`.github/workflows/ci.yml`) are in. The 10 locked eval
queries pass (`eval/run_eval.py`). Not built yet: the AWS Terraform deploy
and the recorded walkthrough. This section gets replaced with the real
architecture diagram, setup steps, and measured eval numbers (DP-9) — no
numbers are claimed here until they're measured.
