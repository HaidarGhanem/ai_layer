from llama_index.core import VectorStoreIndex
from llama_index.core.vector_stores import MetadataFilters
from services.retrieval.retriever import RetrieverService

class ToolRetriever:
    def __init__(
        self,
        index: VectorStoreIndex,
        similarity_top_k: int = 3,
        filters: MetadataFilters | None = None
    ):
        self.retreiver = RetrieverService(
            index=index,
            similarity_top_k=similarity_top_k,
            filters=filters
        )

    def retrieve(self, query: str):
        return self.retreiver.retrieve(query)