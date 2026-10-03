from dataclasses import dataclass 
from typing import Optional 
from services.embedding.provider import EmbeddingProvider

@dataclass
class EmbeddingConfiguration:
    provider: EmbeddingProvider
    model: str
    api_key: Optional[str] = None
    base_url: Optional[str] = None