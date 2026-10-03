from services.config import get_env
from services.vectors.configuration import VectorStoreConfiguration
from services.vectors.profile import VectorStoreProfile
from services.vectors.provider import VectorStoreProvider

def get_default_profiles():
    return {
        "simple": VectorStoreProfile(
            name="simple",
            configuration=VectorStoreConfiguration(
                provider=VectorStoreProvider.SIMPLE,
                collection_name=get_env("VECTOR_COLLECTION_NAME"),
            ),
        ),
        "pgvector": VectorStoreProfile(
            name="pgvector",
            configuration=VectorStoreConfiguration(
                provider=VectorStoreProvider.PGVECTOR,
                database=get_env("PGVECTOR_DATABASE"),
                host=get_env("PGVECTOR_HOST"),
                port=int(get_env("PGVECTOR_PORT")),
                password=get_env("PGVECTOR_PASSWORD"),
                user=get_env("PGVECTOR_USER"),
                table_name=get_env("PGVECTOR_TABLE_NAME"),
                dimension=int(get_env("PGVECTOR_DIMENSION")),
            )
        ),
        "tools": VectorStoreProfile(
            name="tools",
            configuration=VectorStoreConfiguration(
                provider=VectorStoreProvider.PGVECTOR,
                database=get_env("PGVECTOR_DATABASE"),
                host=get_env("PGVECTOR_HOST"),
                port=int(get_env("PGVECTOR_PORT")),
                password=get_env("PGVECTOR_PASSWORD"),
                user=get_env("PGVECTOR_USER"),
                table_name=get_env("TOOL_VECTOR_TABLE_NAME"),
                dimension=int(get_env("PGVECTOR_DIMENSION")),
            ),
        ),
    }