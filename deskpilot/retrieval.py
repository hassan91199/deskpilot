"""Chunking, similarity search, and the `search_docs` tool.

The vector store is a small Protocol so unit tests can use
`InMemoryVectorStore` instead of a real Postgres+pgvector connection
(`deskpilot.pgvector_store.PgVectorStore`, used by `deskpilot.ingest` and at
runtime). Docs in this project are already short, so one chunk == one doc;
there's no sub-document splitting to get wrong.
"""

import math
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from typing import Protocol

# Below this cosine similarity, the brief's "answer only from retrieved
# chunks... no guessing" rule kicks in: treat it as no confident answer.
DEFAULT_SIMILARITY_THRESHOLD = 0.4

EmbedFn = Callable[[Sequence[str]], list[list[float]]]


@dataclass(frozen=True)
class Chunk:
    id: str
    doc_id: str
    doc_title: str
    text: str


@dataclass(frozen=True)
class ScoredChunk:
    chunk: Chunk
    similarity: float


@dataclass(frozen=True)
class RetrievalResult:
    confident: bool
    chunks: list[ScoredChunk]


def chunk_docs(docs: Sequence[dict]) -> list[Chunk]:
    return [
        Chunk(id=doc["id"], doc_id=doc["id"], doc_title=doc["title"], text=doc["body"])
        for doc in docs
    ]


def _cosine_similarity(a: Sequence[float], b: Sequence[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


class VectorStore(Protocol):
    def upsert(self, chunks: Sequence[Chunk], embeddings: Sequence[Sequence[float]]) -> None: ...

    def search(self, query_embedding: Sequence[float], top_k: int) -> list[ScoredChunk]: ...


class InMemoryVectorStore:
    """Cosine-similarity search over Python lists. Unit-test double for
    `PgVectorStore` — no network, no process outside this one."""

    def __init__(self) -> None:
        self._rows: list[tuple[Chunk, Sequence[float]]] = []

    def upsert(self, chunks: Sequence[Chunk], embeddings: Sequence[Sequence[float]]) -> None:
        self._rows = list(zip(chunks, embeddings))

    def search(self, query_embedding: Sequence[float], top_k: int = 4) -> list[ScoredChunk]:
        scored = [
            ScoredChunk(chunk, _cosine_similarity(query_embedding, embedding))
            for chunk, embedding in self._rows
        ]
        scored.sort(key=lambda sc: sc.similarity, reverse=True)
        return scored[:top_k]


def search_docs(
    query: str,
    store: VectorStore,
    embed_fn: EmbedFn,
    top_k: int = 4,
    threshold: float = DEFAULT_SIMILARITY_THRESHOLD,
) -> RetrievalResult:
    (query_embedding,) = embed_fn([query])
    results = store.search(query_embedding, top_k=top_k)
    if not results or results[0].similarity < threshold:
        return RetrievalResult(confident=False, chunks=[])
    return RetrievalResult(confident=True, chunks=results)
