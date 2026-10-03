from llama_index.embeddings.ollama import OllamaEmbedding
from services.embedding.provider import EmbeddingProvider
from services.embedding.configuration import EmbeddingConfiguration

class Embedding:
    def __init__(self, configuration: EmbeddingConfiguration):
        self.configuration = configuration  
        self.model = self._create_model()

    def _create_model(self):
        if self.configuration.provider == EmbeddingProvider.OLLAMA:
            return OllamaEmbedding(
                model_name=self.configuration.model, 
                base_url=self.configuration.base_url
            )

        raise ValueError(
            f"Provider {self.configuration.provider} is not supported")

    def embed_text(self, text: str) -> list[float]:
        return self.model.get_text_embedding(text)

    def embed_query(self, query: str) -> list[float]:
        return self.model.get_query_embedding(query)

    def  embed_batch(self, batch: list[str]) -> list[list[float]]:
        return self.model.get_text_embedding_batch(batch)