# from services.context.in_memory import InMemory
# from services.context.manager import ContextManager
# from services.context.builder import ContextBuilder
# from services.context.configuration import ContextConfiguration

# from services.retrieval.retriever import RetrieverService

# from services.LLM.manager import LLMManager

# from services.loop.tools.registry import ToolRegistry
# from services.loop.tools.calculator import calculate

# from services.documents.document import DocumentService
# from services.embedding.manager import EmbeddingManager
# from services.ingestion.pipeline import IngestionService
# from services.vectors.manager import VectorStoreManager
# from services.indexing.index import IndexService

# from services.brain.brain import Brain


# # ============================================================
# # Embedding / Vector Store
# # ============================================================

# embedding_manager = EmbeddingManager()
# vector_manager = VectorStoreManager()

# embedding = embedding_manager.get_embedding("default")

# vector_store = vector_manager.get_store(
#     "pgvector"
# )


# # ============================================================
# # Documents
# # ============================================================

# document_service = DocumentService()

# documents = [

#     document_service.create(
#         text="Odoo is an ERP system.",
#         metadata={
#             "type": "knowledge",
#             "source": "test",
#         },
#     ),

#     document_service.create(
#         text="Customers in Odoo are represented by res.partner.",
#         metadata={
#             "type": "model",
#             "model": "res.partner",
#         },
#     ),

#     document_service.create(
#         text="Sales orders in Odoo are represented by sale.order.",
#         metadata={
#             "type": "model",
#             "model": "sale.order",
#         },
#     ),

# ]


# # ============================================================
# # Ingestion
# # ============================================================

# pipeline = IngestionService(
#     transformations=[
#         embedding.model
#     ]
# )

# nodes = pipeline.run(
#     documents=documents
# )


# # ============================================================
# # Index
# # ============================================================

# index_service = IndexService(
#     embedding=embedding,
#     vector_store=vector_store,
# )

# index = index_service.create(
#     nodes
# )


# # ============================================================
# # Retriever
# # ============================================================

# retriever_service = RetrieverService(
#     index=index,
#     similarity_top_k=3,
# )


# # ============================================================
# # LLM
# # ============================================================

# llm_manager = LLMManager()


# # ============================================================
# # Memory
# # ============================================================

# memory = InMemory()


# # ============================================================
# # Context Configuration
# # ============================================================

# context_configuration = ContextConfiguration(
#     max_history_tokens=100
# )


# # ============================================================
# # Context Builder
# # ============================================================

# context_builder = ContextBuilder(
#     configuration=context_configuration
# )


# # ============================================================
# # Context Manager
# # ============================================================

# context_manager = ContextManager(
#     memory=memory,
#     builder=context_builder,
# )


# # ============================================================
# # Tool Registry
# # ============================================================

# tool_registry = ToolRegistry()

# tool_registry.register(
#     calculate
# )


# # ============================================================
# # Brain
# # ============================================================

# brain = Brain(
#     manager=llm_manager,
#     retriever=retriever_service,
#     tool_registry=tool_registry,
#     context_manager=context_manager,
# )


# # ============================================================
# # FIRST REQUEST
# # ============================================================

# response = brain.process(
#     session_id="test-session",
#     question="My name is Haidar.",
# )

# print(
#     "\nFIRST RESPONSE:"
# )

# print(
#     response
# )


# print(
#     "\nMEMORY AFTER FIRST REQUEST:"
# )

# print(
#     memory.get("test-session")
# )


# # ============================================================
# # SECOND REQUEST
# # ============================================================

# response = brain.process(
#     session_id="test-session",
#     question="What is my name?",
# )

# print(
#     "\nSECOND RESPONSE:"
# )

# print(
#     response
# )


# print(
#     "\nMEMORY AFTER SECOND REQUEST:"
# )

# print(
#     memory.get("test-session")
# )
from langchain_core.messages import HumanMessage, AIMessage

from services.context.in_memory import InMemory
from services.context.builder import ContextBuilder
from services.context.configuration import ContextConfiguration
from services.context.manager import ContextManager


memory = InMemory()

configuration = ContextConfiguration(
    max_history_tokens=30
)

builder = ContextBuilder(
    configuration=configuration
)

context_manager = ContextManager(
    memory=memory,
    builder=builder,
)


memory.save(
    "test",
    [
        HumanMessage(
            content="Message one " * 10
        ),
        AIMessage(
            content="Message two " * 10
        ),
        HumanMessage(
            content="Message three " * 10
        ),
    ],
)


context = context_manager.build(
    session_id="test",
    question="What is happening?",
)


print("FULL MEMORY:")
print(memory.get("test"))

print("\nCONTEXT SENT TO WORKFLOW:")
print(context.messages)