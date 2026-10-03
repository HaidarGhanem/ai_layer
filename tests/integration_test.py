# ============================================================
# Generic Tool System - Full Integration Test
# ============================================================


# ============================================================
# Tool
# ============================================================

from services.loop.tools.calculator import calculate
from services.loop.tools.current_time import get_current_time


# ============================================================
# Tool System
# ============================================================

from services.tools.register import ToolRegistry
from services.tools.definition import ToolDefinition
from services.tools.catalog import ToolCatalog
from services.tools.catalog_builder import ToolCatalogBuilder
from services.tools.document_builder import ToolDocumentBuilder
from services.tools.indexer import ToolIndexer
from services.tools.retriever import ToolRetriever
from services.tools.resolver import ToolResolver
from services.tools.selector import ToolSelector
from services.tools.selection import ToolSelectionPolicy


# ============================================================
# Existing Infrastructure
# ============================================================

from services.documents.document import DocumentService
from services.ingestion.pipeline import IngestionService
from services.embedding.manager import EmbeddingManager
from services.vectors.manager import VectorStoreManager
from services.indexing.index import IndexService


# ============================================================
# Loop
# ============================================================

from services.LLM.manager import LLMManager
from services.loop.loop import Loop


# ============================================================
# Helper
# ============================================================

def print_section(title: str):

    print("\n")
    print("=" * 60)
    print(title)
    print("=" * 60)


# ============================================================
# 1. Direct Tool Test
# ============================================================

print_section(
    "1. DIRECT TOOL TEST"
)


calculator_result = calculate.invoke(
    {
        "expression": "8 * 944"
    }
)

print(
    "calculate:",
    calculator_result
)


time_result = get_current_time.invoke({})

print(
    "get_current_time:",
    time_result
)


assert calculator_result == "7552"

assert isinstance(
    time_result,
    str,
)

print("\nDIRECT TOOLS: PASS")


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


all_registered_tools = (
    tool_registry.get_all()
)


print(
    "REGISTERED TOOLS:"
)

for tool in all_registered_tools:
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

assert (
    tool_registry.get("calculate")
    is calculate
)

assert (
    tool_registry.get("get_current_time")
    is get_current_time
)

assert len(
    all_registered_tools
) == 2


print("\nTOOL REGISTRY: PASS")


# ============================================================
# 3. Tool Definition
# ============================================================

print_section(
    "3. TOOL DEFINITIONS"
)


catalog_builder = ToolCatalogBuilder()

definitions = []


for tool in all_registered_tools:

    definition = catalog_builder.build(
        tool
    )

    definitions.append(
        definition
    )

    print(
        "\nNAME:",
        definition.name
    )

    print(
        "\nDESCRIPTION:",
        definition.description
    )

    print(
        "\nINPUT SCHEMA:",
        definition.input_schema
    )

    print(
        "\nMETADATA:",
        definition.metadata
    )


assert all(
    isinstance(
        definition,
        ToolDefinition
    )
    for definition in definitions
)

assert len(
    definitions
) == 2


print("\nTOOL DEFINITIONS: PASS")


# ============================================================
# 4. Tool Catalog
# ============================================================

print_section(
    "4. TOOL CATALOG"
)


catalog = ToolCatalog()


for definition in definitions:

    catalog.add(
        definition
    )


catalog_tools = (
    catalog.get_all()
)


print(
    "CATALOG TOOLS:"
)

for definition in catalog_tools:

    print(
        "-",
        definition.name
    )


assert len(
    catalog_tools
) == 2


assert (
    catalog.get("calculate")
    is not None
)

assert (
    catalog.get("get_current_time")
    is not None
)


print("\nTOOL CATALOG: PASS")


# ============================================================
# 5. Tool Documents
# ============================================================

print_section(
    "5. TOOL DOCUMENTS"
)


document_service = DocumentService()


document_builder = ToolDocumentBuilder(
    document_service=document_service
)


tool_documents = []


for definition in catalog_tools:

    document = document_builder.build(
        definition
    )

    tool_documents.append(
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
    tool_documents
) == 2


for document in tool_documents:

    assert (
        document.metadata["type"]
        == "tool"
    )

    assert (
        "tool_name"
        in document.metadata
    )


print("\nTOOL DOCUMENTS: PASS")


# ============================================================
# 6. Embedding
# ============================================================

print_section(
    "6. TOOL EMBEDDING"
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
    "NUMBER OF NODES:",
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
    ) > 0


print("\nTOOL EMBEDDING: PASS")


# ============================================================
# 7. Tool Vector Store
# ============================================================

print_section(
    "7. TOOL VECTOR STORE / INDEX"
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


print(
    "TOOL INDEX CREATED:"
)

print(
    tool_index
)


assert tool_index is not None


print("\nTOOL VECTOR STORE / INDEX: PASS")


# ============================================================
# 8. Tool Retriever
# ============================================================

print_section(
    "8. TOOL RETRIEVER"
)


tool_retriever = ToolRetriever(
    index=tool_index,
    similarity_top_k=5,
)


queries = [

    "I need to calculate 8 multiplied by 944",

    "I want to perform a mathematical calculation",

    "What time is it right now?",
]


retrieval_results = {}


for query in queries:

    print(
        "\nQUERY:",
        query
    )

    results = tool_retriever.retrieve(
        query
    )

    retrieval_results[query] = results

    for result in results:

        print(
            "TOOL:",
            result.node.metadata.get(
                "tool_name"
            )
        )

        print(
            "SCORE:",
            result.score
        )


print("\nTOOL RETRIEVER: PASS")


# ============================================================
# 9. Tool Resolver
# ============================================================

print_section(
    "9. TOOL RESOLVER"
)


resolver = ToolResolver(
    registry=tool_registry
)


calculate_results = tool_retriever.retrieve(
    "I need to calculate 8 multiplied by 944"
)


resolved_tools = resolver.resolve(
    calculate_results
)


print(
    "RESOLVED TOOLS:"
)

for tool in resolved_tools:

    print(
        "-",
        tool.name
    )


assert len(
    resolved_tools
) > 0


assert any(
    tool.name == "calculate"
    for tool in resolved_tools
)


print("\nTOOL RESOLVER: PASS")


# ============================================================
# 10. Selection Policy
# ============================================================

print_section(
    "10. TOOL SELECTION POLICY"
)


policy = ToolSelectionPolicy(
    max_tools=1
)


calculate_candidates = (
    tool_retriever.retrieve(
        "I need to calculate 8 multiplied by 944"
    )
)


selected_candidates = policy.select(
    calculate_candidates
)


print(
    "SELECTED CANDIDATES:"
)

for result in selected_candidates:

    print(
        "-",
        result.node.metadata.get(
            "tool_name"
        ),
        "score=",
        result.score
    )


assert len(
    selected_candidates
) <= 1


print("\nSELECTION POLICY: PASS")


# ============================================================
# 11. Tool Selector
# ============================================================

print_section(
    "11. TOOL SELECTOR"
)


selector = ToolSelector(
    retriever=tool_retriever,
    registry=tool_registry,
    policy=ToolSelectionPolicy(
        max_tools=2
    ),
)


calculate_tools = selector.select(
    "Calculate 8 multiplied by 944"
)


print(
    "QUERY:",
    "Calculate 8 multiplied by 944"
)

print(
    "SELECTED TOOLS:"
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


time_tools = selector.select(
    "What time is it right now?"
)


print(
    "\nQUERY:",
    "What time is it right now?"
)

print(
    "SELECTED TOOLS:"
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


print("\nTOOL SELECTOR: PASS")


# ============================================================
# 12. Dynamic Loop Test - Calculation
# ============================================================

print_section(
    "12. DYNAMIC LOOP - CALCULATION"
)


llm_manager = LLMManager()


loop = Loop(
    llm=llm_manager.get_adapter(
        "loop"
    ),
    tool_selector=selector,
)


loop_result = loop.run(
    question="Calculate 8 multiplied by 944",
    history=[],
)


print(
    "LOOP RESULT:"
)

print(
    loop_result
)


assert loop_result.content

print(
    "\nDYNAMIC CALCULATION LOOP: PASS"
)


# ============================================================
# 13. Dynamic Loop Test - Current Time
# ============================================================

print_section(
    "13. DYNAMIC LOOP - CURRENT TIME"
)


loop_result = loop.run(
    question="What time is it right now?",
    history=[],
)


print(
    "LOOP RESULT:"
)

print(
    loop_result
)


assert loop_result.content

print(
    "\nDYNAMIC TIME LOOP: PASS"
)


# ============================================================
# FINAL RESULT
# ============================================================

print_section(
    "FINAL RESULT"
)

print(
    "ALL GENERIC TOOL SYSTEM TESTS PASSED"
)