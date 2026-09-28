"""Thin OpenAI embeddings wrapper. Always patched in tests (AGENTS.md: no
network calls in the default suite) — the only place that calls this for
real is `deskpilot.ingest` and, at query time, the agent loop.
"""

from collections.abc import Sequence

from openai import OpenAI

EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_DIM = 1536


def embed_texts(texts: Sequence[str]) -> list[list[float]]:
    client = OpenAI()
    response = client.embeddings.create(model=EMBEDDING_MODEL, input=list(texts))
    return [item.embedding for item in response.data]
