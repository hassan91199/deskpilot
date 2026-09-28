import unittest
from unittest.mock import MagicMock, patch

from deskpilot.agent import ToolCall
from deskpilot.llm import CHAT_MODEL, chat_completion


class ChatCompletionTests(unittest.TestCase):
    @patch("deskpilot.llm.OpenAI")
    def test_returns_content_when_no_tool_calls(self, mock_openai_cls):
        mock_client = MagicMock()
        mock_openai_cls.return_value = mock_client
        mock_client.chat.completions.create.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content="Hello there", tool_calls=None))]
        )

        result = chat_completion([{"role": "user", "content": "hi"}], [])

        self.assertEqual(result.content, "Hello there")
        self.assertEqual(result.tool_calls, [])
        mock_client.chat.completions.create.assert_called_once_with(
            model=CHAT_MODEL,
            messages=[{"role": "user", "content": "hi"}],
            tools=[],
            tool_choice="auto",
        )

    @patch("deskpilot.llm.OpenAI")
    def test_parses_tool_calls_with_json_arguments(self, mock_openai_cls):
        mock_client = MagicMock()
        mock_openai_cls.return_value = mock_client
        fake_tool_call = MagicMock(id="call_1")
        fake_tool_call.function.name = "search_docs"
        fake_tool_call.function.arguments = '{"query": "rotate api key"}'
        mock_client.chat.completions.create.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content=None, tool_calls=[fake_tool_call]))]
        )

        result = chat_completion([{"role": "user", "content": "how do I rotate a key?"}], [])

        self.assertIsNone(result.content)
        self.assertEqual(
            result.tool_calls,
            [ToolCall(id="call_1", name="search_docs", arguments={"query": "rotate api key"})],
        )


if __name__ == "__main__":
    unittest.main()
