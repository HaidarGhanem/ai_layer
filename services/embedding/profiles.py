from services.config import get_env
from services.embedding.configuration import EmbeddingConfiguration
from services.embedding.provider import EmbeddingProvider
from services.embedding.profile import EmbeddingProfile

def get_default_profiles():
    return {
        "default": EmbeddingProfile(
            name="default",
            configuration=EmbeddingConfiguration(
                provider=EmbeddingProvider.OLLAMA,
                model="nomic-embed-text:latest",
                base_url="http://localhost:11434",
            )
                
        )
    }