from llama_index.core import VectorStoreIndex
from llama_index.core.vector_stores import MetadataFilters

class RetrieverService:
    def __init__(
            self, 
            index: VectorStoreIndex, 
            similarity_top_k: int = 2,
            filters: MetadataFilters | None = None
            ):
        self.index = index
        self.similarity_top_k = similarity_top_k
        self.filters = filters

        self.retriever= self.index.as_retriever(similarity_top_k=self.similarity_top_k, filters=self.filters)

    def retrieve(self, query: str):
        return self.retriever.retrieve(query)