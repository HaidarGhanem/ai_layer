from llama_index.core import StorageContext, VectorStoreIndex
class IndexService:
    def __init__(self, embedding, vector_store):
        self.embedding = embedding
        self.vector_store = vector_store

    def create(self, nodes):

        storage_context = StorageContext.from_defaults(
            vector_store=self.vector_store.get_backend()
        )

        return VectorStoreIndex(
            nodes=nodes,
            storage_context=storage_context,
            embed_model=self.embedding.model,
        )