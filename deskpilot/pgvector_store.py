"""Real Postgres+pgvector implementation of `deskpilot.retrieval.VectorStore`.

Deliberately untouched by the default unit-test gate (AGENTS.md: no network
calls, ever, in `tests/`) — this is exercised by `deskpilot.ingest` and the
opt-in eval harness against the local docker-compose Postgres, not by
`scripts/test.sh`.
"""

from collections.abc import Sequence

import psycopg
from pgvector.psycopg import register_vector

from deskpilot.embeddings import EMBEDDING_DIM
from deskpilot.retrieval import Chunk, ScoredChunk


class PgVectorStore:  # pragma: no cover
    def __init__(self, dsn: str) -> None:
        self._dsn = dsn

    def _connect(self, *, register: bool = True) -> psycopg.Connection:
        conn = psycopg.connect(self._dsn)
        if register:
            register_vector(conn)
        return conn

    def ensure_schema(self) -> None:
        # The `vector` type doesn't exist until the extension is created, and
        # register_vector() needs the type to already exist — so this first
        # connection must skip registration.
        with self._connect(register=False) as conn:
            conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
            conn.execute(
                f"""
                CREATE TABLE IF NOT EXISTS doc_chunks (
                    id TEXT PRIMARY KEY,
                    doc_id TEXT NOT NULL,
                    doc_title TEXT NOT NULL,
                    text TEXT NOT NULL,
                    embedding VECTOR({EMBEDDING_DIM}) NOT NULL
                )
                """
            )

    def upsert(self, chunks: Sequence[Chunk], embeddings: Sequence[Sequence[float]]) -> None:
        with self._connect() as conn:
            for chunk, embedding in zip(chunks, embeddings):
                conn.execute(
                    """
                    INSERT INTO doc_chunks (id, doc_id, doc_title, text, embedding)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO UPDATE SET
                        doc_id = EXCLUDED.doc_id,
                        doc_title = EXCLUDED.doc_title,
                        text = EXCLUDED.text,
                        embedding = EXCLUDED.embedding
                    """,
                    (chunk.id, chunk.doc_id, chunk.doc_title, chunk.text, embedding),
                )

    def search(self, query_embedding: Sequence[float], top_k: int = 4) -> list[ScoredChunk]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT id, doc_id, doc_title, text, 1 - (embedding <=> %s::vector) AS similarity
                FROM doc_chunks
                ORDER BY embedding <=> %s::vector
                LIMIT %s
                """,
                (query_embedding, query_embedding, top_k),
            ).fetchall()
        return [
            ScoredChunk(Chunk(id=row[0], doc_id=row[1], doc_title=row[2], text=row[3]), row[4])
            for row in rows
        ]
