# See AGENTS.md

All conventions for this repo — code-change workflow, test layers, style,
and the ClickUp task workflow — live in [AGENTS.md](AGENTS.md). It's kept
agent-agnostic on purpose (Claude Code, OpenCode, Codex, or anything else
should be able to pick this project up from that one file). Nothing
Claude-specific belongs in this file; it exists only because Claude Code
looks for `CLAUDE.md` by name.
