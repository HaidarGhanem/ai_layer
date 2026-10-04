from typing import Any, Literal

from pydantic import BaseModel, Field


StreamEventType = Literal[
    "token",
    "tool_started",
    "tool_finished",
    "confirmation_required",
    "completed",
    "error",
]


class StreamEvent(BaseModel):
    type: StreamEventType
    data: dict[str, Any] = Field(default_factory=dict)
