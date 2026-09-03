"""Shared test fixtures/helpers."""

from langchain_core.messages import AIMessage


class FakeLLM:
    """Stand-in for a chat model in tests — no network calls, no API key."""

    def __init__(self, responses: list[str]) -> None:
        self._responses = list(responses)

    def invoke(self, _input) -> AIMessage:
        content = self._responses.pop(0) if self._responses else ""
        return AIMessage(content=content)
