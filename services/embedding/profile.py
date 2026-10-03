from dataclasses import dataclass
from services.embedding.configuration import EmbeddingConfiguration

@dataclass
class EmbeddingProfile: 
    name: str 
    configuration: EmbeddingConfiguration