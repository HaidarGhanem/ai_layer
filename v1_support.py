from langgraph.checkpoint.memory import InMemorySaver
from llama_index.core import StorageContext, VectorStoreIndex
from llama_index.core.vector_stores import SimpleVectorStore

from services.LLM.manager import LLMManager
from services.embedding.manager import EmbeddingManager
from services.ingestion.pipeline import IngestionService
from services.documents.document import DocumentService
from services.retrieval.retriever import RetrieverService
from services.tools.register import ToolRegistry
from services.tools.catalog_builder import ToolCatalogBuilder
from services.tools.document_builder import ToolDocumentBuilder
from services.tools.retriever import ToolRetriever
from services.tools.selector import ToolSelector

from services.loop.tools.calculator import calculate
from services.loop.tools.current_time import get_current_time

from services.risk.level import RiskLevel
from services.risk.policy import RiskPolicy
from services.risk.engine import RiskEngine

from services.context.configuration import ContextConfiguration

from services.brain.brain import Brain


def _build_index(nodes, embedding):
    vector_store = SimpleVectorStore()
    storage_context = StorageContext.from_defaults(
        vector_store=vector_store,
    )
    return VectorStoreIndex(
        nodes=nodes,
        storage_context=storage_context,
        embed_model=embedding.model,
    )


def build_demo_brain(
    calculate_risk: RiskLevel = RiskLevel.LOW,
    current_time_risk: RiskLevel = RiskLevel.LOW,
) -> Brain:
    """Build a local, dependency-light Brain for V1 tests and API demo.

    The demo uses SimpleVectorStore instead of PostgreSQL so it remains
    self-contained. It still exercises the same tool retrieval and RAG
    retrieval abstractions used by the real Core.
    """
    embedding = EmbeddingManager().get_embedding("default")
    document_service = DocumentService()
    ingestion = IngestionService(
        transformations=[embedding.model]
    )

    # ------------------------------------------------------------
    # Tool system
    # ------------------------------------------------------------
    catalog_builder = ToolCatalogBuilder()
    tool_registry = ToolRegistry()

    tool_definitions = []
    for tool in (calculate, get_current_time):
        definition = catalog_builder.build(tool)
        tool_definitions.append(definition)
        tool_registry.register(tool, definition)

    document_builder = ToolDocumentBuilder(
        document_service=document_service
    )
    tool_documents = [
        document_builder.build(definition)
        for definition in tool_definitions
    ]
    tool_nodes = ingestion.run(documents=tool_documents)
    tool_index = _build_index(tool_nodes, embedding)
    tool_retriever = ToolRetriever(
        index=tool_index,
        similarity_top_k=3,
    )
    tool_selector = ToolSelector(
        retriever=tool_retriever,
        registry=tool_registry,
    )

    # ------------------------------------------------------------
    # Knowledge / RAG
    # ------------------------------------------------------------
    knowledge_document = document_service.create(
        text=(
            "In Odoo, customers are represented by the "
            "res.partner model."
        ),
        metadata={
            "type": "knowledge",
            "topic": "odoo",
        },
        document_id="demo:odoo:customers",
    )
    knowledge_nodes = ingestion.run(
        documents=[knowledge_document]
    )
    knowledge_index = _build_index(
        knowledge_nodes,
        embedding,
    )
    knowledge_retriever = RetrieverService(
        index=knowledge_index,
        similarity_top_k=2,
    )

    # ------------------------------------------------------------
    # Risk / Context / Brain
    # ------------------------------------------------------------
    risk_engine = RiskEngine(
        policy=RiskPolicy(
            tool_levels={
                "calculate": calculate_risk,
                "get_current_time": current_time_risk,
            }
        )
    )

    return Brain(
        manager=LLMManager(),
        retriever=knowledge_retriever,
        tool_selector=tool_selector,
        tool_registry=tool_registry,
        risk_engine=risk_engine,
        checkpointer=InMemorySaver(),
        context_manager=None,
        context_configuration=ContextConfiguration(
            max_tool_tokens=1500,
        ),
    )
