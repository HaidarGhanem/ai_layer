from dataclasses import dataclass
from typing import Optional
from services.LLM.provider import LLMProvider


@dataclass
class LLMConfiguration:
    provider: LLMProvider
    model: str
    temperature: float = 0.2
    api_key: Optional[str] = None
    base_url: Optional[str] = None
