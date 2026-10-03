from typing import Any, Literal 
from pydantic import BaseModel, Field

class BrainMetadataResponse(BaseModel):
    response: dict[str, Any] = Field(default_factory=dict)
    usage: dict[str, Any] = Field(default_factory=dict)

class BrainResponse(BaseModel):
    content: str 
    data: Any | None = None
    display_type: Literal["table","text","card"] = "text"
    metadata: BrainMetadataResponse = Field(default_factory=BrainMetadataResponse)