# Demo generator

Regenerates `docs/demo/demo.mp4` (narrated, captioned) per
`personal-docs/strategies/demo_assets_playbook.md`'s Step 2. Re-run this
whenever the UI or the narration wording changes — the recording is real,
not scripted/faked, so it has to be redone against the live app, not edited
by hand.

## Setup (once)

```bash
python3 -m venv demo/.venv
demo/.venv/bin/pip install edge-tts playwright
```

## Run

1. Start the real stack (see the root README's "Run it"): Postgres + ingest,
   the API on :8000, the frontend on :3000. The database should be empty of
   demo tickets before recording — `docker exec deskpilot-postgres-1 psql -U
   deskpilot -d deskpilot -c "DELETE FROM tickets;"` if a prior run left any.
2. `demo/.venv/bin/python demo/synthesize.py` — synthesizes narration audio
   + per-word caption timings from `script.json` into `build/narration.json`
   (clips cached in `build/clips/`).
3. `demo/.venv/bin/python demo/record.py` — records the real UI, paced
   against each scene's narration duration, into `build/raw.webm` +
   `build/cues.json`. Also drops fresh screenshots into `build/shots/`.
4. `python3 demo/compose.py` (system ffmpeg, no venv needed) — composes the
   final `docs/demo/demo.mp4`: captions bar, narration, loudness
   normalization, one ffmpeg pass.

`build/` is gitignored — regeneratable, not a deliverable. `script.json` and
the four scripts are the deliverable; `docs/demo/demo.mp4` (and any
screenshots pulled from `build/shots/`) are committed separately.

Always watch the final video with sound before using it — sync and
loudness are checked programmatically (frame sampling, `volumedetect`), not
by ear, per the playbook's own caveat.
