# from services.RAG.rag import RAGService 
from services.retrieval.retriever import RetrieverService
from services.indexing.index import IndexService
from services.LLM.manager import LLMManager
from services.documents.document import DocumentService
from services.embedding.manager import EmbeddingManager 
from services.ingestion.pipeline import IngestionService 
from services.vectors.manager import VectorStoreManager
from services.brain.brain import Brain 

llm_manager = LLMManager()
embed_manager = EmbeddingManager()
vector_manager = VectorStoreManager()

llm = llm_manager.get_adapter("rag")
embed = embed_manager.get_embedding("default")
vector_store = vector_manager.get_store("pgvector")

document_service = DocumentService()

documents = [

    document_service.create(
        text="Odoo is an ERP system.",
        metadata={
            "type": "knowledge",
            "source": "test",
        },
    ),

    document_service.create(
        text="Customers in Odoo are represented by res.partner.",
        metadata={
            "type": "model",
            "model": "res.partner",
        },
    ),

    document_service.create(
        text="Sales orders in Odoo are represented by sale.order.",
        metadata={
            "type": "model",
            "model": "sale.order",
        },
    ),

]

pipeline = IngestionService(transformations=[embed.model])

nodes = pipeline.run(documents=documents)

index_service = IndexService(embed, vector_store)

index = index_service.create(nodes)

retriever = RetrieverService(
    index=index,
    similarity_top_k=2
)

# rag = RAGService(
#     retriever=retriever,
#     llm=llm
# )
question = "Explain how Odoo structure models for customers and what res.partner means."
# question = "How are customers represented in Odoo?"
# results = rag.retrieve(question)

# print("Results:", len(results))

# for result in results:
#     print("\nText:")
#     print(result.node.text)

#     print("Score:")
#     print(result.score)

#     print("Metadata:")
#     print(result.node.metadata)

#     print("--------------------------------")
#     print("--------------------------------")


# print("--------------------------------")
# Generation
# response = rag.generate(
#     question=question,
#     results=results,
# )
# print(response.content)

from services.loop.tools.registry import ToolRegistry
from services.loop.tools.calculator import calculate

tool_registry = ToolRegistry() 
tool_registry.register(calculate)
brain = Brain(
    manager=llm_manager,
    retriever=retriever,
    tool_registry=tool_registry
)
question =  "Execute this multiply to calc 8 * 944"
response = brain.process(
   question
)

print(response)