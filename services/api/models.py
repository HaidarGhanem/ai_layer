from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ProcessRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    question: str = Field(..., min_length=1, max_length=10000)
    session_id: str = Field(..., min_length=1, max_length=256)

    @field_validator("question", "session_id")
    @classmethod
    def strip_required_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Value must not be empty.")
        return value


class ResumeRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    session_id: str = Field(..., min_length=1, max_length=256)
    approved: bool

    @field_validator("session_id")
    @classmethod
    def strip_session_id(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Session ID must not be empty.")
        return value


class ErrorResponse(BaseModel):
    code: str
    message: str
    details: Any | None = None
    request_id: str


class HealthResponse(BaseModel):
    status: Literal["ok"]
    service: str
    version: str
    langsmith_enabled: bool
