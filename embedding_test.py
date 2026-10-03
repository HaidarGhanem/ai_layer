from services.documents.document import DocumentService
from services.embedding.manager import EmbeddingManager
from services.ingestion.pipeline import IngestionService
from services.vectors.manager import VectorStoreManager
from services.indexing.index import IndexService
from services.retrieval.retriever import RetrieverService
from llama_index.core.vector_stores import MetadataFilter, MetadataFilters, FilterOperator

embedding_manager = EmbeddingManager()
vector_manager = VectorStoreManager()

embedding = embedding_manager.get_embedding("default")
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

pipeline = IngestionService(transformations=[embedding.model])

nodes = pipeline.run(documents=documents)

print("Nodes:", len(nodes))

index_service = IndexService(embedding, vector_store)

index = index_service.create(nodes)

print("Index:", index)

retriever_service = RetrieverService(
    index=index,
    similarity_top_k=3,
)

results = retriever_service.retrieve("How are customers represented in Odoo?")

print("\nResults:")

for result in results:
    print(result.node.text)
    print(result.node.metadata)
    print("Score:", result.score)

model_filter = MetadataFilter(
    key="type",
    value="model",
    operator=FilterOperator.EQ
)

filters = MetadataFilters(filters=[model_filter])

retriever_service = RetrieverService(
    index=index,
    similarity_top_k=3,
    filters=filters
)

results = retriever_service.retrieve("How are customers represented in Odoo?")

print("\nResults:")

for result in results:
    print(result.node.text)
    print(result.node.metadata)
    print("Score:", result.score)


# from services.documents.document import DocumentService
# from services.vectors.manager import VectorStoreManager
# from services.embedding.manager import EmbeddingManager
# from services.ingestion.pipeline import IngestionService

# embedding_manager = EmbeddingManager()
# vector_manager = VectorStoreManager()

# embedding = embedding_manager.get_embedding("default")
# vector_store = vector_manager.get_store("simple")

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

# pipeline = IngestionService(
#     transformations=[
#         embedding.model
#     ],
# )

# nodes = pipeline.run(documents=documents)

# vector_store.add(nodes)

# print("Nodes added:", len(nodes))

# query_vector = embedding.embed_query("How are customers represented in Odoo?")

# from llama_index.core.vector_stores import VectorStoreQuery

# query = VectorStoreQuery(
#     query_embedding=query_vector,
#     similarity_top_k=2
# )

# result = vector_store.query(query)


# print("\nResult IDs:")
# print(result.ids)

# print("\nSimilarities:")
# print(result.similarities)


# from llama_index.core import Document, VectorStoreIndex 
# from llama_index.core.ingestion import IngestionPipeline
# from llama_index.core.node_parser import SentenceSplitter
# from services.embedding.manager import EmbeddingManager

# manager = EmbeddingManager()

# embedding = manager.get_embedding("default")

# document = Document(
#     text="""
#         Odoo is an ERP system.

#         Customers are represented by res.partner.

#         Sales are represented by sale.order.

#         Products are represented by product.product.
#     """,
#     metadata={
#         "source": "odoo",
#         "type": "knowledge"
#     }
# )

# pipeline = IngestionPipeline(
#     transformations=[
#         SentenceSplitter(
#             chunk_size=30,
#             chunk_overlap=10
#         ),
#         embedding.model
#     ],

# )

# nodes = pipeline.run(documents=[document])

# index = VectorStoreIndex(
#     nodes=nodes,
#     embed_model=embedding.model
# )

# retriever = index.as_retriever(similarity_top_k=2)

# query = "How are customers represented in Odoo?"

# results = retriever.retrieve(query)


# print("Number of results:", len(results))


# for result in results:
#     print("------")
#     print("Node:", result.node.text)
#     print("Score:", result.score)
#     print("Metadata:", result.node.metadata)


# from llama_index.core import Document
# from llama_index.core.ingestion import IngestionPipeline
# from llama_index.core.node_parser import SentenceSplitter
# from llama_index.core.vector_stores import SimpleVectorStore, VectorStoreQuery
# from services.embedding.manager import EmbeddingManager


# manager = EmbeddingManager()
# embedding = manager.get_embedding("default")


# document = Document(
#     text="""
#         Odoo is an ERP system.

#         Customers are represented by res.partner.

#         Sales are represented by sale.order.

#         Products are represented by product.product.
#     """,
#     metadata={
#         "source": "odoo",
#         "type": "knowledge"
#     }
# )

# pipeline = IngestionPipeline(
#     transformations=[
#         SentenceSplitter(
#             chunk_size=30,
#             chunk_overlap=10
#         ),
#         embedding.model
#     ],

# )

# nodes = pipeline.run(documents=[document])

# vector_store = SimpleVectorStore()
# vector_store.add(nodes)


# query_vector = embedding.embed_query("How are customers represented in Odoo?")

# query = VectorStoreQuery(
#     query_embedding=query_vector,
#     similarity_top_k=3
# )

# result = vector_store.query(query) 

# print("Result IDs:")
# print(result.ids)

# print("Similarities:")
# print(result.similarities)



# from llama_index.core import Document
# from llama_index.core.schema import TextNode


# document = Document(
#     text="Customer model in Odoo",
#     metadata={
#         "type": "model",
#         "model": "res.partner",
#         "module": "base",
#     },
# )

# node = TextNode(
#     text=document.text,
#     metadata=document.metadata,
# )

# print("DOCUMENT")
# print(type(document))
# print(document.text)
# print(document.metadata)

# print("\nNODE")
# print(type(node))
# print(node.text)
# print(node.metadata)
# print(node.node_id)

# from llama_index.core.schema import TextNode


# node = TextNode(
#     text="Customer model in Odoo",
#     metadata={
#         "type": "model",
#         "model": "res.partner",
#         "module": "base",
#     },
# )

# print(type(node))
# print(node.text)
# print(node.metadata)
# print(node.node_id)


# from llama_index.core import Document


# document = Document(
#     text="Customer model in Odoo",
#     metadata={
#         "type": "model",
#         "model": "res.partner",
#         "module": "base",
#     },
# )

# print(document.text)
# print(document.metadata)


# from services.embedding.manager import EmbeddingManager

# manager = EmbeddingManager()
# embedding = manager.get_embedding("default")

# texts = [
#     "Odoo customer information",
#     "Odoo sales order information",
#     "Odoo employee information",
# ]

# vectors = embedding.embed_batch(texts)

# print(type(vectors))
# print(len(vectors))

# for index, vector in enumerate(vectors):
#     print(f"Vector {index}:")
#     print(type(vector))
#     print(len(vector))
#     print(vector[:5])

