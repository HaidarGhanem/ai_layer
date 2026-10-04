from dataclasses import dataclass, field
from typing import Any

@dataclass
class ToolDefinition:
    name: str
    description: str
    input_schema: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
    tool_id: str | None = None