from services.loop.tools.calculator import calculate

from services.tools.catalog import ToolCatalog
from services.tools.catalog_builder import ToolCatalogBuilder
from services.tools.document_builder import ToolDocumentBuilder
from services.tools.indexer import ToolIndexer

from services.documents.document import DocumentService
from services.ingestion.pipeline import IngestionService

from services.embedding.manager import EmbeddingManager
from services.vectors.manager import VectorStoreManager
from services.indexing.index import IndexService

from services.tools.resolver import ToolResolver
from services.tools.register import ToolRegistry
from services.LLM.manager import LLMManager

from services.loop.loop import Loop
llm_manager = LLMManager()
# ============================================================
# Embedding
# ============================================================

embedding_manager = EmbeddingManager()

embedding = embedding_manager.get_embedding(
    "default"
)


# ============================================================
# Tool Catalog
# ============================================================

catalog = ToolCatalog()

catalog_builder = ToolCatalogBuilder()

definition = catalog_builder.build(
    calculate
)

catalog.add(
    definition
)


# ============================================================
# Document Builder
# ============================================================

document_service = DocumentService()

document_builder = ToolDocumentBuilder(
    document_service=document_service
)


# ============================================================
# Ingestion
# ============================================================

ingestion = IngestionService(
    transformations=[
        embedding.model
    ]
)


# ============================================================
# Tool Indexer
# ============================================================

tool_indexer = ToolIndexer(
    catalog=catalog,
    document_builder=document_builder,
    ingestion=ingestion,
)


tool_nodes = tool_indexer.index()


# ============================================================
# Tool Vector Store
# ============================================================

vector_manager = VectorStoreManager()

tool_vector_store = vector_manager.get_store(
    "tools"
)


# ============================================================
# Tool Index
# ============================================================

tool_index_service = IndexService(
    embedding=embedding,
    vector_store=tool_vector_store,
)

tool_index = tool_index_service.create(
    tool_nodes
)


# ============================================================
# Test
# ============================================================

from services.tools.retriever import ToolRetriever


tool_retriever = ToolRetriever(
    index=tool_index,
    similarity_top_k=3,
)


from services.tools.selector import ToolSelector




tool_registry = ToolRegistry()
tool_registry.register(calculate)

tool_selector = ToolSelector(
    retriever=tool_retriever,
    registry=tool_registry,
)

loop = Loop(
    llm=llm_manager.get_adapter("loop"),
    tool_selector=tool_selector,
)


result = loop.run(
    question="Calculate 8 multiplied by 944",
    history=[],
)


print("CONTENT:")
print(result.content)
# from services.loop.tools.calculator import calculate

# from services.tools.catalog import ToolCatalog
# from services.tools.catalog_builder import ToolCatalogBuilder
# from services.tools.document_builder import ToolDocumentBuilder
# from services.tools.indexer import ToolIndexer

# from services.documents.document import DocumentService
# from services.ingestion.pipeline import IngestionService

# from services.embedding.manager import EmbeddingManager


# # -----------------------------------------
# # Embedding
# # -----------------------------------------

# embedding_manager = EmbeddingManager()

# embedding = embedding_manager.get_embedding(
#     "default"
# )


# # -----------------------------------------
# # Tool Catalog
# # -----------------------------------------

# catalog = ToolCatalog()

# catalog_builder = ToolCatalogBuilder()

# definition = catalog_builder.build(
#     calculate
# )

# catalog.add(
#     definition
# )


# # -----------------------------------------
# # Document Builder
# # -----------------------------------------

# document_service = DocumentService()

# document_builder = ToolDocumentBuilder(
#     document_service=document_service
# )


# # -----------------------------------------
# # Ingestion
# # -----------------------------------------

# ingestion = IngestionService(
#     transformations=[
#         embedding.model
#     ]
# )


# # -----------------------------------------
# # Tool Indexer
# # -----------------------------------------

# tool_indexer = ToolIndexer(
#     catalog=catalog,
#     document_builder=document_builder,
#     ingestion=ingestion,
# )


# # -----------------------------------------
# # Build + Embed
# # -----------------------------------------

# nodes = tool_indexer.index()


# # -----------------------------------------
# # Test
# # -----------------------------------------

# print("NUMBER OF NODES:")
# print(len(nodes))

# print("\nFIRST NODE TEXT:")
# print(nodes[0].text)

# print("\nEMBEDDING DIMENSION:")
# print(len(nodes[0].embedding))

# print("\nMETADATA:")
# print(nodes[0].metadata)

# from services.loop.tools.calculator import calculate
# from services.tools.catalog_builder import ToolCatalogBuilder
# from services.tools.document_builder import ToolDocumentBuilder
# from services.documents.document import DocumentService


# catalog_builder = ToolCatalogBuilder()

# document_service = DocumentService()

# document_builder = ToolDocumentBuilder(
#     document_service=document_service,
# )

# definition = catalog_builder.build(
#     calculate
# )

# document = document_builder.build(
#     definition
# )

# print("DOCUMENT TEXT:")
# print(document.text)

# print("\nDOCUMENT METADATA:")
# print(document.metadata)

# from services.loop.tools.calculator import calculate

# from services.tools.catalog import ToolCatalog
# from services.tools.catalog_builder import ToolCatalogBuilder


# builder = ToolCatalogBuilder()

# catalog = ToolCatalog()

# definition = builder.build(
#     calculate
# )

# catalog.add(
#     definition
# )

# print(
#     "NAME:"
# )

# print(
#     definition.name
# )

# print(
#     "\nDESCRIPTION:"
# )

# print(
#     definition.description
# )

# print(
#     "\nINPUT SCHEMA:"
# )

# print(
#     definition.input_schema
# )

# print(
#     "\nMETADATA:"
# )

# print(
#     definition.metadata
# )