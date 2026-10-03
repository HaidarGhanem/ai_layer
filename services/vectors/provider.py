from enum import Enum 

class VectorStoreProvider(str, Enum):
    SIMPLE = "simple"
    PGVECTOR = "pgvector"