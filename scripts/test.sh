#!/bin/sh
# Full local test gate: lint, then the whole suite under coverage with the
# configured floor (pyproject.toml [tool.coverage.report] fail_under).
# Docker's `test` entrypoint mode runs this too, so CI and local match.
# The eval harness (eval/run_eval.py) hits real OpenAI + Postgres and is
# never part of this gate — run it separately, on demand.
set -e
cd "$(dirname "$0")/.."

# Docker has python on PATH; locally prefer the repo venv if present.
if [ -x ".venv/bin/python" ]; then
    PYTHON=.venv/bin/python
else
    PYTHON=python
fi

"$PYTHON" -m ruff check deskpilot eval tests scripts
"$PYTHON" -m ruff format --check deskpilot eval tests scripts
"$PYTHON" -m coverage run -m unittest discover -s tests
"$PYTHON" -m coverage report
