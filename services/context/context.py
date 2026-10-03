from dataclasses import dataclass, field 
from typing import Any 
from langchain_core.messages import BaseMessage

@dataclass
class AIContext:
    session_id: str
    question: str
    history: list[BaseMessage] = field(
        default_factory=list
    )
    messages: list[BaseMessage] = field(
        default_factory=list
    )
    retrieved_context: list[Any] = field(default_factory=list)
    tool_results: list[dict[str, Any]] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)