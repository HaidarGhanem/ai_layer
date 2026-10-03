# ============================================================
# Router + Brain - Full Integration Test
# ============================================================


# ============================================================
# LlamaIndex / Existing Infrastructure
# ============================================================

from services.documents.document import DocumentService
from services.embedding.manager import EmbeddingManager
from services.ingestion.pipeline import IngestionService
from services.indexing.index import IndexService
from services.retrieval.retriever import RetrieverService
from services.vectors.manager import VectorStoreManager


# ============================================================
# LLM
# ============================================================

from services.LLM.manager import LLMManager


# ============================================================
# Router
# ============================================================

from services.router.router import Router


# ============================================================
# Brain
# ============================================================

from services.brain.brain import Brain


# ============================================================
# Context / Memory
# ============================================================

from services.context.in_memory import InMemory
from services.context.manager import ContextManager
from services.context.builder import ContextBuilder
from services.context.configuration import ContextConfiguration


# ============================================================
# Tools
# ============================================================

from services.loop.tools.calculator import calculate
from services.loop.tools.current_time import get_current_time

from services.tools.register import ToolRegistry
from services.tools.catalog import ToolCatalog
from services.tools.catalog_builder import ToolCatalogBuilder
from services.tools.document_builder import ToolDocumentBuilder
from services.tools.indexer import ToolIndexer
from services.tools.retriever import ToolRetriever
from services.tools.selector import ToolSelector
from services.tools.selection import ToolSelectionPolicy


# ============================================================
# LangChain Messages
# ============================================================

from langchain_core.messages import (
    HumanMessage,
    AIMessage,
)


# ============================================================
# Helper
# ============================================================

def print_section(title: str):

    print("\n")
    print("=" * 70)
    print(title)
    print("=" * 70)


# ============================================================
# 1. LLM Manager
# ============================================================

print_section(
    "1. LLM MANAGER"
)

llm_manager = LLMManager()

print(
    "LLM MANAGER: PASS"
)


# ============================================================
# 2. RAG Infrastructure
# ============================================================

print_section(
    "2. RAG SETUP"
)

embedding_manager = EmbeddingManager()

embedding = embedding_manager.get_embedding(
    "default"
)

vector_manager = VectorStoreManager()

# We use the existing general vector store
# for the RAG test.
vector_store = vector_manager.get_store(
    "simple"
)

document_service = DocumentService()


documents = [

    document_service.create(
        text="Odoo is an ERP system.",
        metadata={
            "type": "knowledge",
            "source": "brain-test",
        },
    ),

    document_service.create(
        text="Customers in Odoo are represented by res.partner.",
        metadata={
            "type": "model",
            "model": "res.partner",
            "source": "brain-test",
        },
    ),

    document_service.create(
        text="Sales orders in Odoo are represented by sale.order.",
        metadata={
            "type": "model",
            "model": "sale.order",
            "source": "brain-test",
        },
    ),

]


rag_ingestion = IngestionService(
    transformations=[
        embedding.model
    ]
)

rag_nodes = rag_ingestion.run(
    documents=documents
)


rag_index_service = IndexService(
    embedding=embedding,
    vector_store=vector_store,
)

rag_index = rag_index_service.create(
    rag_nodes
)


rag_retriever = RetrieverService(
    index=rag_index,
    similarity_top_k=3,
)


print(
    "RAG INDEX CREATED"
)

print(
    "RAG NODES:",
    len(rag_nodes)
)


assert len(rag_nodes) == 3

print(
    "RAG SETUP: PASS"
)


# ============================================================
# 3. Generic Tool Registry
# ============================================================

print_section(
    "3. TOOL REGISTRY"
)


tool_registry = ToolRegistry()

tool_registry.register(
    calculate
)

tool_registry.register(
    get_current_time
)


registered_tools = (
    tool_registry.get_all()
)


print(
    "REGISTERED TOOLS:"
)

for tool in registered_tools:

    print(
        "-",
        tool.name
    )


assert tool_registry.has(
    "calculate"
)

assert tool_registry.has(
    "get_current_time"
)

assert len(
    registered_tools
) == 2


print(
    "TOOL REGISTRY: PASS"
)


# ============================================================
# 4. Tool Catalog
# ============================================================

print_section(
    "4. TOOL CATALOG"
)


catalog = ToolCatalog()

catalog_builder = ToolCatalogBuilder()


for tool in registered_tools:

    definition = catalog_builder.build(
        tool
    )

    catalog.add(
        definition
    )


catalog_definitions = (
    catalog.get_all()
)


for definition in catalog_definitions:

    print(
        "\nTOOL:",
        definition.name
    )

    print(
        "DESCRIPTION:",
        definition.description
    )

    print(
        "INPUT SCHEMA:",
        definition.input_schema
    )


assert len(
    catalog_definitions
) == 2


assert (
    catalog.get("calculate")
    is not None
)

assert (
    catalog.get("get_current_time")
    is not None
)


print(
    "\nTOOL CATALOG: PASS"
)


# ============================================================
# 5. Tool Documents + Embedding
# ============================================================

print_section(
    "5. TOOL DOCUMENTS + EMBEDDING"
)


tool_document_service = DocumentService()

tool_document_builder = ToolDocumentBuilder(
    document_service=tool_document_service
)


tool_ingestion = IngestionService(
    transformations=[
        embedding.model
    ]
)


tool_indexer = ToolIndexer(
    catalog=catalog,
    document_builder=tool_document_builder,
    ingestion=tool_ingestion,
)


tool_nodes = tool_indexer.index()


print(
    "TOOL NODES:",
    len(tool_nodes)
)


for node in tool_nodes:

    print(
        "\nTOOL:",
        node.metadata.get(
            "tool_name"
        )
    )

    print(
        "VECTOR DIMENSION:",
        len(node.embedding)
    )


assert len(
    tool_nodes
) == 2


for node in tool_nodes:

    assert node.embedding is not None

    assert len(
        node.embedding
    ) == 768


print(
    "\nTOOL EMBEDDING: PASS"
)


# ============================================================
# 6. Dedicated Tool Vector Store + Index
# ============================================================

print_section(
    "6. TOOL VECTOR STORE + INDEX"
)


tool_vector_store = vector_manager.get_store(
    "tools"
)


tool_index_service = IndexService(
    embedding=embedding,
    vector_store=tool_vector_store,
)


tool_index = tool_index_service.create(
    tool_nodes
)


assert tool_index is not None


print(
    "TOOL INDEX: CREATED"
)

print(
    "TOOL VECTOR STORE + INDEX: PASS"
)


# ============================================================
# 7. Tool Retriever
# ============================================================

print_section(
    "7. TOOL RETRIEVER"
)


tool_retriever = ToolRetriever(
    index=tool_index,
    similarity_top_k=5,
)


calculate_results = tool_retriever.retrieve(
    "I need to calculate 8 multiplied by 944"
)


print(
    "CALCULATION QUERY RESULTS:"
)

for result in calculate_results:

    print(
        result.node.metadata.get(
            "tool_name"
        ),
        "->",
        result.score
    )


assert len(
    calculate_results
) > 0


time_results = tool_retriever.retrieve(
    "What time is it right now?"
)


print(
    "\nTIME QUERY RESULTS:"
)

for result in time_results:

    print(
        result.node.metadata.get(
            "tool_name"
        ),
        "->",
        result.score
    )


assert len(
    time_results
) > 0


print(
    "\nTOOL RETRIEVER: PASS"
)


# ============================================================
# 8. Tool Selector
# ============================================================

print_section(
    "8. TOOL SELECTOR"
)


tool_selector = ToolSelector(
    retriever=tool_retriever,
    registry=tool_registry,
    policy=ToolSelectionPolicy(
        max_tools=2
    ),
)


selected_calculate_tools = (
    tool_selector.select(
        "Calculate 8 multiplied by 944"
    )
)


print(
    "CALCULATION SELECTED TOOLS:"
)

for tool in selected_calculate_tools:

    print(
        "-",
        tool.name
    )


assert any(
    tool.name == "calculate"
    for tool in selected_calculate_tools
)


selected_time_tools = (
    tool_selector.select(
        "What time is it right now?"
    )
)


print(
    "\nTIME SELECTED TOOLS:"
)

for tool in selected_time_tools:

    print(
        "-",
        tool.name
    )


assert any(
    tool.name == "get_current_time"
    for tool in selected_time_tools
)


print(
    "\nTOOL SELECTOR: PASS"
)


# ============================================================
# 9. Router Standalone Tests
# ============================================================

print_section(
    "9. ROUTER TESTS"
)


router = Router(
    llm_manager
)


# ------------------------------------------------------------
# 9.1 Chat
# ------------------------------------------------------------

chat_router_result = router.route(
    question="Hello, how are you?",
    history=[],
)


print(
    "\nCHAT TEST:"
)

print(
    "ROUTE:",
    chat_router_result.route
)

print(
    "CONFIDENCE:",
    chat_router_result.confidence
)

print(
    "CLARIFICATION:",
    chat_router_result.needs_clarification
)


assert (
    chat_router_result.route
    == "chat"
)

assert (
    chat_router_result.confidence
    > 0.5
)


# ------------------------------------------------------------
# 9.2 RAG
# ------------------------------------------------------------

rag_router_result = router.route(
    question="What customers exist in Odoo?",
    history=[],
)


print(
    "\nRAG TEST:"
)

print(
    "ROUTE:",
    rag_router_result.route
)

print(
    "CONFIDENCE:",
    rag_router_result.confidence
)

print(
    "CLARIFICATION:",
    rag_router_result.needs_clarification
)


assert (
    rag_router_result.route
    == "rag"
)

assert (
    rag_router_result.confidence
    > 0.5
)


# ------------------------------------------------------------
# 9.3 Loop
# ------------------------------------------------------------

loop_router_result = router.route(
    question="Calculate 8 multiplied by 944.",
    history=[],
)


print(
    "\nLOOP TEST:"
)

print(
    "ROUTE:",
    loop_router_result.route
)

print(
    "CONFIDENCE:",
    loop_router_result.confidence
)

print(
    "CLARIFICATION:",
    loop_router_result.needs_clarification
)


assert (
    loop_router_result.route
    == "loop"
)

assert (
    loop_router_result.confidence
    > 0.5
)


# ------------------------------------------------------------
# 9.4 Router + History
# ------------------------------------------------------------

history_router_result = router.route(
    question="What is my name?",
    history=[
        HumanMessage(
            content="My name is Haidar."
        ),
        AIMessage(
            content="Nice to meet you, Haidar."
        ),
    ],
)


print(
    "\nHISTORY-AWARE TEST:"
)

print(
    "ROUTE:",
    history_router_result.route
)

print(
    "CONFIDENCE:",
    history_router_result.confidence
)

print(
    "CLARIFICATION:",
    history_router_result.needs_clarification
)


assert (
    history_router_result.route
    == "chat"
)

assert (
    history_router_result.confidence
    > 0.5
)


print(
    "\nROUTER TESTS: PASS"
)


# ============================================================
# 10. Context / Memory
# ============================================================

print_section(
    "10. CONTEXT / MEMORY"
)


memory = InMemory()


context_configuration = (
    ContextConfiguration(
        max_history_tokens=100
    )
)


context_builder = ContextBuilder(
    configuration=context_configuration
)


context_manager = ContextManager(
    memory=memory,
    builder=context_builder,
)


# First request

context = context_manager.build(
    session_id="context-test",
    question="My name is Haidar.",
)


assert len(
    context.history
) == 0


assert len(
    context.messages
) == 1


context_manager.save_response(
    context=context,
    response="Nice to meet you, Haidar.",
)


# Second request

context_2 = context_manager.build(
    session_id="context-test",
    question="What is my name?",
)


print(
    "FULL MEMORY:"
)

print(
    context_2.history
)


print(
    "\nCONTEXT SENT TO WORKFLOW:"
)

print(
    context_2.messages
)


assert len(
    context_2.history
) == 2


assert len(
    context_2.messages
) == 3


print(
    "\nCONTEXT / MEMORY: PASS"
)


# ============================================================
# 11. Build Brain
# ============================================================

print_section(
    "11. BRAIN CREATION"
)


brain = Brain(
    manager=llm_manager,
    retriever=rag_retriever,
    tool_selector=tool_selector,
    context_manager=context_manager,
)


print(
    "BRAIN CREATED"
)


print(
    "BRAIN CREATION: PASS"
)


# ============================================================
# 12. Brain - Chat First Request
# ============================================================

print_section(
    "12. BRAIN CHAT - FIRST REQUEST"
)


response = brain.process(
    session_id="brain-chat-test",
    question="My name is Haidar.",
)


print(
    "RESPONSE:"
)

print(
    response
)


assert response.content
assert response.display_type == "text"


print(
    "\nBRAIN CHAT FIRST REQUEST: PASS"
)


# ============================================================
# 13. Brain - Chat With Memory
# ============================================================

print_section(
    "13. BRAIN CHAT - MEMORY"
)


response = brain.process(
    session_id="brain-chat-test",
    question="What is my name?",
)


print(
    "RESPONSE:"
)

print(
    response
)


assert response.content

assert (
    "haidar"
    in response.content.lower()
)


print(
    "\nBRAIN CHAT MEMORY: PASS"
)


# ============================================================
# 14. Brain - RAG
# ============================================================

print_section(
    "14. BRAIN RAG"
)


response = brain.process(
    session_id="brain-rag-test",
    question="How are customers represented in Odoo?",
)


print(
    "RESPONSE:"
)

print(
    response
)


assert response.content

assert (
    "res.partner"
    in response.content
)


print(
    "\nBRAIN RAG: PASS"
)


# ============================================================
# 15. Brain - Dynamic Loop / Calculator
# ============================================================

print_section(
    "15. BRAIN LOOP - CALCULATOR"
)


response = brain.process(
    session_id="brain-loop-calc-test",
    question="Calculate 8 multiplied by 944.",
)


print(
    "RESPONSE:"
)

print(
    response
)


assert response.content

assert (
    "7552"
    in response.content
)


print(
    "\nBRAIN LOOP CALCULATOR: PASS"
)


# ============================================================
# 16. Brain - Dynamic Loop / Current Time
# ============================================================

print_section(
    "16. BRAIN LOOP - CURRENT TIME"
)


response = brain.process(
    session_id="brain-loop-time-test",
    question="What time is it right now?",
)


print(
    "RESPONSE:"
)

print(
    response
)


assert response.content


print(
    "\nBRAIN LOOP CURRENT TIME: PASS"
)


# ============================================================
# 17. Memory After Brain Tests
# ============================================================

print_section(
    "17. BRAIN MEMORY VERIFICATION"
)


brain_memory = memory.get(
    "brain-chat-test"
)


print(
    "BRAIN CHAT MEMORY:"
)

for message in brain_memory:

    print(
        message
    )


assert len(
    brain_memory
) == 4


print(
    "\nBRAIN MEMORY: PASS"
)


# ============================================================
# 18. Session Isolation
# ============================================================

print_section(
    "18. SESSION ISOLATION"
)


memory_a = InMemory()

manager_a = ContextManager(
    memory=memory_a,
    builder=ContextBuilder(
        configuration=ContextConfiguration(
            max_history_tokens=100
        )
    ),
)


context_a = manager_a.build(
    session_id="session-a",
    question="My name is Haidar.",
)


manager_a.save_response(
    context=context_a,
    response="Nice to meet you.",
)


context_b = manager_a.build(
    session_id="session-b",
    question="Hello.",
)


print(
    "SESSION A:"
)

print(
    memory_a.get("session-a")
)


print(
    "\nSESSION B:"
)

print(
    memory_a.get("session-b")
)


assert len(
    memory_a.get("session-a")
) == 2


assert len(
    memory_a.get("session-b")
) == 0


print(
    "\nSESSION ISOLATION: PASS"
)


# ============================================================
# 19. Brain Streaming
# ============================================================

print_section(
    "19. BRAIN STREAMING"
)


stream_result = brain.stream(
    session_id="brain-stream-test",
    question="Explain what an ERP system is.",
)


stream_content = []


for chunk in stream_result:

    if hasattr(chunk, "content"):

        if chunk.content:

            stream_content.append(
                str(chunk.content)
            )


stream_text = "".join(
    stream_content
)


print(
    "STREAM CONTENT:"
)

print(
    stream_text
)


assert stream_text


print(
    "\nBRAIN STREAMING: PASS"
)


# ============================================================
# FINAL SUMMARY
# ============================================================

print_section(
    "FINAL RESULT"
)


print(
    "ALL ROUTER + BRAIN INTEGRATION TESTS PASSED"
)