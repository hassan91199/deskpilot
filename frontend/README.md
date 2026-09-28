# DeskPilot frontend

Next.js chat widget with a trace side panel (retrieved sources, tool calls,
tool results) for the DeskPilot support agent. See the repo root `AGENTS.md`
for project-wide conventions — this file only covers running the frontend
itself.

## Running locally

Needs the backend running first (repo root):

```sh
docker compose up -d postgres
.venv/bin/uvicorn deskpilot.api:app --reload
```

Then, in this directory:

```sh
npm run dev
```

Open the printed local URL (usually http://localhost:3000; Next.js falls
back to 3001 if 3000 is taken). The backend's CORS allowlist in
`deskpilot/api.py` covers both.

`NEXT_PUBLIC_API_BASE_URL` overrides the backend URL (default
`http://localhost:8000`) if you need to point at something else.

Deploy: per the AWS/Terraform standard in
`strategies/demo_deployment_strategy.md` (one cloud, no Vercel) — not wired
up yet, that's DP-8.
