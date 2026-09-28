import unittest
from unittest.mock import MagicMock, patch

from deskpilot.embeddings import EMBEDDING_MODEL, embed_texts


class EmbedTextsTests(unittest.TestCase):
    @patch("deskpilot.embeddings.OpenAI")
    def test_returns_vectors_in_request_order(self, mock_openai_cls):
        mock_client = MagicMock()
        mock_openai_cls.return_value = mock_client
        mock_client.embeddings.create.return_value = MagicMock(
            data=[MagicMock(embedding=[0.1, 0.2]), MagicMock(embedding=[0.3, 0.4])]
        )

        result = embed_texts(["a", "b"])

        self.assertEqual(result, [[0.1, 0.2], [0.3, 0.4]])
        mock_client.embeddings.create.assert_called_once_with(
            model=EMBEDDING_MODEL, input=["a", "b"]
        )


if __name__ == "__main__":
    unittest.main()
