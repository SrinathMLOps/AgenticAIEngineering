from typing import Any


class ConversationBuffer:
    """Stores the full message history for the agent loop."""

    def __init__(self) -> None:
        self._messages: list[dict[str, Any]] = []

    def add_user(self, content: str) -> None:
        self._messages.append({"role": "user", "content": content})

    def add_assistant(self, content: list[dict]) -> None:
        self._messages.append({"role": "assistant", "content": content})

    def add_tool_result(self, tool_use_id: str, result: str, is_error: bool = False) -> None:
        tool_result_block = {
            "type": "tool_result",
            "tool_use_id": tool_use_id,
            "content": result,
            "is_error": is_error,
        }
        # Tool results must go in a user message
        self._messages.append({"role": "user", "content": [tool_result_block]})

    def get_messages(self) -> list[dict[str, Any]]:
        return self._messages

    def summary(self) -> str:
        turns = len([m for m in self._messages if m["role"] == "assistant"])
        return f"{turns} agent turn(s), {len(self._messages)} total messages"
