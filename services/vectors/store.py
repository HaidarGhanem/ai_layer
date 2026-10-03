from llama_index.core.vector_stores import SimpleVectorStore
from services.vectors.configuration import VectorStoreConfiguration
from services.vectors.provider import VectorStoreProvider
from llama_index.vector_stores.postgres import PGVectorStore


class VectorStore:
    def __init__(self, configuration: VectorStoreConfiguration):
        self.configuration = configuration
        self.store = self._create_store()

    def _create_store(self):
        if self.configuration.provider == VectorStoreProvider.SIMPLE:
            return SimpleVectorStore()

        if self.configuration.provider == VectorStoreProvider.PGVECTOR:
            return PGVectorStore.from_params(
                database=self.configuration.database,
                host=self.configuration.host,
                password=self.configuration.password,
                port=self.configuration.port,
                user=self.configuration.user,
                table_name=self.configuration.table_name,
                embed_dim=self.configuration.dimension,
            )

        raise ValueError(
            f"Provider {self.configuration.provider} is not supported"
        )

    def add(self, nodes):
        return self.store.add(nodes)

    def query(self, query):
        return self.store.query(query)

    def get_backend(self):
        return self.store