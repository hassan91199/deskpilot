"""Real OpenAI chat-completions wrapper with function calling.

Returns `deskpilot.agent`'s own `AssistantMessage`/`ToolCall` dataclasses
instead of raw SDK objects, so `run_turn` never depends on the OpenAI SDK's
response shape — matching `deskpilot.embeddings.embed_texts`, this stays
unit-testable by patching `OpenAI` (see `tests/test_llm.py`), no network in
the default suite.
"""

import json
from collections.abc import Sequence

from openai import OpenAI

from deskpilot.agent import AssistantMessage, ToolCall

CHAT_MODEL = "gpt-4o-mini"


def chat_completion(messages: Sequence[dict], tool_schemas: Sequence[dict]) -> AssistantMessage:
    client = OpenAI()
    response = client.chat.completions.create(
        model=CHAT_MODEL,
        messages=list(messages),
        tools=list(tool_schemas),
        tool_choice="auto",
    )
    message = response.choices[0].message
    tool_calls = [
        ToolCall(id=tc.id, name=tc.function.name, arguments=json.loads(tc.function.arguments))
        for tc in (message.tool_calls or [])
    ]
    return AssistantMessage(content=message.content, tool_calls=tool_calls)
