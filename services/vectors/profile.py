from dataclasses import dataclass
from services.vectors.configuration import VectorStoreConfiguration

@dataclass
class VectorStoreProfile:
    name: str
    configuration: VectorStoreConfiguration

