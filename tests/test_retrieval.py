import unittest

from deskpilot.retrieval import (
    Chunk,
    InMemoryVectorStore,
    _cosine_similarity,
    chunk_docs,
    search_docs,
)

DOCS = [
    {"id": "a", "title": "Doc A", "category": "x", "body": "alpha text"},
    {"id": "b", "title": "Doc B", "category": "x", "body": "beta text"},
]


class ChunkDocsTests(unittest.TestCase):
    def test_one_chunk_per_doc_preserving_order(self):
        chunks = chunk_docs(DOCS)
        self.assertEqual(
            chunks,
            [
                Chunk(id="a", doc_id="a", doc_title="Doc A", text="alpha text"),
                Chunk(id="b", doc_id="b", doc_title="Doc B", text="beta text"),
            ],
        )


class CosineSimilarityTests(unittest.TestCase):
    def test_zero_vector_is_zero_similarity_not_division_by_zero(self):
        self.assertEqual(_cosine_similarity([0.0, 0.0], [1.0, 0.0]), 0.0)


class InMemoryVectorStoreTests(unittest.TestCase):
    def test_search_ranks_by_cosine_similarity_descending(self):
        store = InMemoryVectorStore()
        store.upsert(chunk_docs(DOCS), [[1.0, 0.0], [0.0, 1.0]])

        results = store.search([1.0, 0.0], top_k=2)

        self.assertEqual([r.chunk.id for r in results], ["a", "b"])
        self.assertAlmostEqual(results[0].similarity, 1.0)
        self.assertAlmostEqual(results[1].similarity, 0.0)

    def test_search_respects_top_k(self):
        store = InMemoryVectorStore()
        store.upsert(chunk_docs(DOCS), [[1.0, 0.0], [0.9, 0.1]])

        results = store.search([1.0, 0.0], top_k=1)

        self.assertEqual(len(results), 1)


class SearchDocsTests(unittest.TestCase):
    def _store_with(self, embeddings):
        store = InMemoryVectorStore()
        store.upsert(chunk_docs(DOCS), embeddings)
        return store

    def test_confident_result_returns_ranked_chunks(self):
        store = self._store_with([[1.0, 0.0], [0.0, 1.0]])

        result = search_docs(
            "query", store, embed_fn=lambda texts: [[1.0, 0.0] for _ in texts], threshold=0.5
        )

        self.assertTrue(result.confident)
        self.assertEqual(result.chunks[0].chunk.doc_title, "Doc A")

    def test_weak_top_similarity_is_not_confident(self):
        store = self._store_with([[1.0, 0.0], [0.0, 1.0]])

        result = search_docs(
            "query", store, embed_fn=lambda texts: [[-1.0, 0.0] for _ in texts], threshold=0.5
        )

        self.assertFalse(result.confident)
        self.assertEqual(result.chunks, [])

    def test_embeds_only_the_query_not_the_docs(self):
        calls = []

        def embed_fn(texts):
            calls.append(list(texts))
            return [[1.0, 0.0] for _ in texts]

        store = self._store_with([[1.0, 0.0], [0.0, 1.0]])
        search_docs("How do I rotate a key?", store, embed_fn=embed_fn)

        self.assertEqual(calls, [["How do I rotate a key?"]])


if __name__ == "__main__":
    unittest.main()
