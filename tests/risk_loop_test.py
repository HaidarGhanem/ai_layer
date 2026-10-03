# ============================================================
# Risk + Loop - Full Integration Test
# ============================================================


# ============================================================
# Tools
# ============================================================

from services.loop.tools.calculator import calculate
from services.loop.tools.current_time import get_current_time

from langchain_core.tools import tool


@tool
def delete_demo_record(record_id: str) -> str:
    """
    Delete a demo record.

    Use this tool only when the user explicitly
    asks to delete a demo record.
    """

    return (
        f"Demo record {record_id} was deleted."
    )


# ============================================================
# LLM
# ============================================================

from services.LLM.manager import LLMManager


# ============================================================
# Generic Tool System
# ============================================================

from services.tools.register import ToolRegistry
from services.tools.catalog import ToolCatalog
from services.tools.catalog_builder import ToolCatalogBuilder
from services.tools.document_builder import ToolDocumentBuilder
from services.tools.indexer import ToolIndexer
from services.tools.retriever import ToolRetriever
from services.tools.selector import ToolSelector
from services.tools.selection import ToolSelectionPolicy


# ============================================================
# Existing Infrastructure
# ============================================================

from services.documents.document import DocumentService
from services.embedding.manager import EmbeddingManager
from services.ingestion.pipeline import IngestionService
from services.vectors.manager import VectorStoreManager
from services.indexing.index import IndexService


# ============================================================
# Risk
# ============================================================

from services.risk.level import RiskLevel
from services.risk.policy import RiskPolicy
from services.risk.engine import RiskEngine


# ============================================================
# Loop
# ============================================================

from services.loop.loop import Loop
from services.loop.state import LoopState


# ============================================================
# LangGraph Checkpointer
# ============================================================

from langgraph.checkpoint.memory import InMemorySaver


# ============================================================
# Helper
# ============================================================

def print_section(title: str):

    print("\n")
    print("=" * 70)
    print(title)
    print("=" * 70)


# ============================================================
# 1. LLM
# ============================================================

print_section(
    "1. LLM MANAGER"
)

llm_manager = LLMManager()

print(
    "LLM MANAGER: PASS"
)


# ============================================================
# 2. Tool Registry
# ============================================================

print_section(
    "2. TOOL REGISTRY"
)


tool_registry = ToolRegistry()

tool_registry.register(
    calculate
)

tool_registry.register(
    get_current_time
)

tool_registry.register(
    delete_demo_record
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

assert tool_registry.has(
    "delete_demo_record"
)

assert len(
    registered_tools
) == 3


print(
    "\nTOOL REGISTRY: PASS"
)


# ============================================================
# 3. Tool Catalog
# ============================================================

print_section(
    "3. TOOL CATALOG"
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


definitions = catalog.get_all()


print(
    "CATALOG:"
)

for definition in definitions:

    print(
        "\nTOOL:",
        definition.name
    )

    print(
        "DESCRIPTION:",
        definition.description
    )

    print(
        "SCHEMA:",
        definition.input_schema
    )


assert len(
    definitions
) == 3


print(
    "\nTOOL CATALOG: PASS"
)


# ============================================================
# 4. Tool Documents
# ============================================================

print_section(
    "4. TOOL DOCUMENTS"
)


document_service = DocumentService()

document_builder = ToolDocumentBuilder(
    document_service=document_service
)


documents = []


for definition in definitions:

    document = document_builder.build(
        definition
    )

    documents.append(
        document
    )

    print(
        "\nTEXT:"
    )

    print(
        document.text
    )

    print(
        "\nMETADATA:"
    )

    print(
        document.metadata
    )


assert len(
    documents
) == 3


print(
    "\nTOOL DOCUMENTS: PASS"
)


# ============================================================
# 5. Embedding
# ============================================================

print_section(
    "5. TOOL EMBEDDING"
)


embedding_manager = EmbeddingManager()

embedding = embedding_manager.get_embedding(
    "default"
)


ingestion = IngestionService(
    transformations=[
        embedding.model
    ]
)


tool_indexer = ToolIndexer(
    catalog=catalog,
    document_builder=document_builder,
    ingestion=ingestion,
)


tool_nodes = tool_indexer.index()


print(
    "TOOL NODES:",
    len(tool_nodes)
)


assert len(
    tool_nodes
) == 3


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

    assert node.embedding is not None

    assert len(
        node.embedding
    ) == 768


print(
    "\nTOOL EMBEDDING: PASS"
)


# ============================================================
# 6. Tool Vector Store / Index
# ============================================================

print_section(
    "6. TOOL VECTOR STORE / INDEX"
)


vector_manager = VectorStoreManager()


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
    "TOOL INDEX CREATED"
)

print(
    "\nTOOL VECTOR STORE / INDEX: PASS"
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


queries = [

    "Calculate 8 multiplied by 944",

    "What time is it right now?",

    "Delete demo record 123",

]


for query in queries:

    print(
        "\nQUERY:",
        query
    )

    results = tool_retriever.retrieve(
        query
    )

    assert len(
        results
    ) > 0

    for result in results:

        print(
            "-",
            result.node.metadata.get(
                "tool_name"
            ),
            "score=",
            result.score
        )


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


# ------------------------------------------------------------
# Calculator Selection
# ------------------------------------------------------------

calculate_tools = (
    tool_selector.select(
        "Calculate 8 multiplied by 944"
    )
)


print(
    "CALCULATION SELECTED TOOLS:"
)

for tool in calculate_tools:

    print(
        "-",
        tool.name
    )


assert any(
    tool.name == "calculate"
    for tool in calculate_tools
)


# ------------------------------------------------------------
# Time Selection
# ------------------------------------------------------------

time_tools = (
    tool_selector.select(
        "What time is it right now?"
    )
)


print(
    "\nTIME SELECTED TOOLS:"
)

for tool in time_tools:

    print(
        "-",
        tool.name
    )


assert any(
    tool.name == "get_current_time"
    for tool in time_tools
)


# ------------------------------------------------------------
# Delete Selection
# ------------------------------------------------------------

delete_tools = (
    tool_selector.select(
        "Delete demo record 123"
    )
)


print(
    "\nDELETE SELECTED TOOLS:"
)

for tool in delete_tools:

    print(
        "-",
        tool.name
    )


assert any(
    tool.name == "delete_demo_record"
    for tool in delete_tools
)


print(
    "\nTOOL SELECTOR: PASS"
)


# ============================================================
# 9. Risk Policy
# ============================================================

print_section(
    "9. RISK POLICY"
)


risk_policy = RiskPolicy(

    tool_levels={

        "calculate":
            RiskLevel.LOW,

        "get_current_time":
            RiskLevel.LOW,

        "delete_demo_record":
            RiskLevel.HIGH,

    },

    blocked_tools={
        "blocked_demo_tool",
    },
)


print(
    "RISK POLICY CREATED"
)

print(
    "\nRISK POLICY: PASS"
)


# ============================================================
# 10. Risk Engine
# ============================================================

print_section(
    "10. RISK ENGINE"
)


risk_engine = RiskEngine(
    policy=risk_policy
)


# ------------------------------------------------------------
# Low Risk
# ------------------------------------------------------------

calculate_decision = (
    risk_engine.check(
        "calculate"
    )
)


print(
    "\nCALCULATE:"
)

print(
    calculate_decision
)


assert (
    calculate_decision.action
    == "allow"
)

assert (
    calculate_decision.risk_level
    == RiskLevel.LOW
)


# ------------------------------------------------------------
# High Risk
# ------------------------------------------------------------

delete_decision = (
    risk_engine.check(
        "delete_demo_record"
    )
)


print(
    "\nDELETE:"
)

print(
    delete_decision
)


assert (
    delete_decision.action
    == "confirm"
)

assert (
    delete_decision.risk_level
    == RiskLevel.HIGH
)


# ------------------------------------------------------------
# Unknown Tool
# ------------------------------------------------------------

unknown_decision = (
    risk_engine.check(
        "unknown_tool"
    )
)


print(
    "\nUNKNOWN TOOL:"
)

print(
    unknown_decision
)


assert (
    unknown_decision.action
    == "confirm"
)

assert (
    unknown_decision.risk_level
    == RiskLevel.MEDIUM
)


# ------------------------------------------------------------
# Blocked Tool
# ------------------------------------------------------------

blocked_decision = (
    risk_engine.check(
        "blocked_demo_tool"
    )
)


print(
    "\nBLOCKED TOOL:"
)

print(
    blocked_decision
)


assert (
    blocked_decision.action
    == "reject"
)

assert (
    blocked_decision.risk_level
    == RiskLevel.CRITICAL
)


print(
    "\nRISK ENGINE: PASS"
)


# ============================================================
# 11. Checkpointer
# ============================================================

print_section(
    "11. CHECKPOINTER"
)


checkpointer = InMemorySaver()

print(
    "CHECKPOINTER CREATED"
)

print(
    "\nCHECKPOINTER: PASS"
)


# ============================================================
# 12. Loop Creation
# ============================================================

print_section(
    "12. LOOP"
)


loop = Loop(

    llm=llm_manager.get_adapter(
        "loop"
    ),

    tool_selector=tool_selector,

    tool_registry=tool_registry,

    risk_engine=risk_engine,

    checkpointer=checkpointer,

)


print(
    "LOOP CREATED"
)

print(
    "\nLOOP CREATION: PASS"
)


# ============================================================
# 13. Low Risk Loop
# ============================================================

print_section(
    "13. LOW RISK LOOP"
)


result = loop.run(

    question=(
        "Calculate 8 multiplied by 944"
    ),

    history=[],

    thread_id="low-risk-thread",

)


print(
    "RESULT:"
)

print(
    result
)


assert (
    result.content
)

assert (
    result.metadata.get(
        "status"
    )
    == "completed"
)


print(
    "\nLOW RISK LOOP: PASS"
)


# ============================================================
# 14. Low Risk Time Loop
# ============================================================

print_section(
    "14. LOW RISK TIME LOOP"
)


result = loop.run(

    question=(
        "What time is it right now?"
    ),

    history=[],

    thread_id="time-risk-thread",

)


print(
    "RESULT:"
)

print(
    result
)


assert (
    result.content
)

assert (
    result.metadata.get(
        "status"
    )
    == "completed"
)


print(
    "\nLOW RISK TIME LOOP: PASS"
)


# ============================================================
# 15. HIGH RISK - INTERRUPT
# ============================================================

print_section(
    "15. HIGH RISK - CONFIRMATION INTERRUPT"
)


delete_thread_id = (
    "delete-confirm-thread"
)


result = loop.run(

    question=(
        "Delete demo record 123"
    ),

    history=[],

    thread_id=delete_thread_id,

)


print(
    "INITIAL RESULT:"
)

print(
    result
)


assert (
    result.metadata.get(
        "status"
    )
    == "waiting_confirmation"
)


assert (
    result.data is not None
)


assert (
    result.data["type"]
    == "confirmation"
)


print(
    "\nINTERRUPT: PASS"
)


# ============================================================
# 16. HIGH RISK - APPROVE
# ============================================================

print_section(
    "16. HIGH RISK - APPROVE"
)


approved_result = loop.resume(

    thread_id=delete_thread_id,

    approved=True,

)


print(
    "APPROVED RESULT:"
)

print(
    approved_result
)


assert (
    approved_result.metadata.get(
        "status"
    )
    == "completed"
)


assert (
    approved_result.content
)


print(
    "\nAPPROVAL / RESUME: PASS"
)


# ============================================================
# 17. HIGH RISK - REJECT
# ============================================================

print_section(
    "17. HIGH RISK - REJECT"
)


reject_thread_id = (
    "delete-reject-thread"
)


reject_result = loop.run(

    question=(
        "Delete demo record 456"
    ),

    history=[],

    thread_id=reject_thread_id,

)


print(
    "INITIAL RESULT:"
)

print(
    reject_result
)


assert (
    reject_result.metadata.get(
        "status"
    )
    == "waiting_confirmation"
)


rejected_result = loop.resume(

    thread_id=reject_thread_id,

    approved=False,

)


print(
    "\nREJECTED RESULT:"
)

print(
    rejected_result
)


assert (
    rejected_result.metadata.get(
        "status"
    )
    == "completed"
)


assert (
    "cancel"
    in rejected_result.content.lower()
    or
    "reject"
    in rejected_result.content.lower()
    or
    "cancelled"
    in rejected_result.content.lower()
)


print(
    "\nREJECTION / RESUME: PASS"
)


# ============================================================
# 18. Final Tool Result Verification
# ============================================================

print_section(
    "18. FINAL STATE VERIFICATION"
)


print(
    "APPROVED RESULT:"
)

print(
    approved_result
)


print(
    "\nREJECTED RESULT:"
)

print(
    rejected_result
)


assert approved_result.content

assert rejected_result.content


print(
    "\nFINAL STATE: PASS"
)


# ============================================================
# FINAL
# ============================================================

print_section(
    "FINAL RESULT"
)


print(
    "ALL RISK + LOOP INTEGRATION TESTS PASSED"
)