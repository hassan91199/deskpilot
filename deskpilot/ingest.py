"""Offline ingest: chunk + embed the seed docs, upsert into pgvector.

Usage: python -m deskpilot.ingest

Real OpenAI + real Postgres — not part of the default test gate, deliberately
excluded from coverage the same way `pgvector_store.py` is.
"""

from deskpilot.config import database_url
from deskpilot.embeddings import embed_texts
from deskpilot.pgvector_store import PgVectorStore
from deskpilot.retrieval import chunk_docs
from deskpilot.seed.docs import DOCS


def main() -> None:  # pragma: no cover
    store = PgVectorStore(database_url())
    store.ensure_schema()

    chunks = chunk_docs(DOCS)
    embeddings = embed_texts([chunk.text for chunk in chunks])
    store.upsert(chunks, embeddings)
    print(f"Ingested {len(chunks)} chunks.")


if __name__ == "__main__":  # pragma: no cover
    main()
