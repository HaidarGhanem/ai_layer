from typing import Any, Literal
from pydantic import BaseModel, Field

class LoopResult(BaseModel):
    content: str
    display_type: Literal['text','card','table'] = 'text'
    data: Any | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
