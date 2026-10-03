from typing import Any, Literal 
from pydantic import BaseModel, Field

class RagResult(BaseModel):
    content: str
    display_type: Literal["table","text","card"]
    usage: dict[str, Any] = Field(default_factory=dict)
    response_metadata: dict[str, Any] = Field(default_factory=dict) 