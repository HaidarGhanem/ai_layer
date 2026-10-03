from services.embedding.configuration import EmbeddingConfiguration
from services.embedding.profiles import get_default_profiles
from services.embedding.embedding import Embedding

class EmbeddingManager:
    def __init__(self):
        self.profiles = get_default_profiles()

    def get_embedding(self, name):
        profile = self.profiles.get(name)

        if not profile:
            raise ValueError(
                f"Embedding {name} not found"
            )
        
        return Embedding(profile.configuration)