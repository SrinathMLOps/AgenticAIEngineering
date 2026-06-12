from pydantic import BaseModel
from typing import Any


class ToolCall(BaseModel):
    id: str
    name: str
    input: dict[str, Any]


class ToolResult(BaseModel):
    tool_use_id: str
    content: str
    is_error: bool = False
