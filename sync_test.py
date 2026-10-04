from services.loop.tools.calculator import calculate

from services.tools.register import ToolRegistry
from services.tools.lifecycle import ToolLifecycle

from services.tools.catalog_builder import ToolCatalogBuilder

from services.tools.document_builder import ToolDocumentBuilder
from services.tools.synchronizer import ToolIndexSynchronizer

from services.documents.document import DocumentService
from services.embedding.manager import EmbeddingManager
from services.ingestion.pipeline import IngestionService
from services.vectors.manager import VectorStoreManager


# ============================================================
# Setup
# ============================================================

registry = ToolRegistry()

lifecycle = ToolLifecycle(
    registry=registry
)

catalog_builder = ToolCatalogBuilder()

document_service = DocumentService()

document_builder = ToolDocumentBuilder(
    document_service=document_service
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

vector_manager = VectorStoreManager()

tool_vector_store = vector_manager.get_store(
    "tools"
)

synchronizer = ToolIndexSynchronizer(
    vector_store=tool_vector_store,
    document_builder=document_builder,
    ingestion=ingestion,
    lifecycle=lifecycle,
)


# ============================================================
# 1. Register Tool
# ============================================================

print("\n================ REGISTER ================")


definition = catalog_builder.build(
    calculate,
    metadata={
        "source": "internal",
    },
)


change, record = lifecycle.register(
    tool=calculate,
    definition=definition,
)


print(
    "CHANGE:",
    change
)

print(
    "VERSION:",
    record.version
)

print(
    "FINGERPRINT:",
    record.fingerprint
)

print(
    "NEEDS REINDEX:",
    lifecycle.needs_reindex(
        "calculate"
    )
)


assert change.value == "added"

assert lifecycle.needs_reindex(
    "calculate"
)


# ============================================================
# 2. First Sync
# ============================================================

print("\n================ FIRST SYNC ================")


result = synchronizer.sync(
    "calculate"
)


print(
    "SYNC RESULT:"
)

print(
    result
)


assert result["status"] == "indexed"

assert result["version"] == 1

assert (
    record.indexed_fingerprint
    == record.fingerprint
)


assert lifecycle.needs_reindex(
    "calculate"
) is False


first_document_id = (
    result["document_id"]
)


print(
    "\nFIRST DOCUMENT ID:",
    first_document_id
)


# ============================================================
# 3. Second Sync - No Changes
# ============================================================

print("\n================ SECOND SYNC ================")


result = synchronizer.sync(
    "calculate"
)


print(
    "SYNC RESULT:"
)

print(
    result
)


assert result["status"] == "unchanged"

assert result["version"] == 1


# ============================================================
# 4. Update Definition
# ============================================================

print("\n================ UPDATE ================")


updated_definition = (
    catalog_builder.build(
        calculate,
        metadata={
            "source": "internal",
            "category": "arithmetic",
        },
    )
)


change, updated_record = (
    lifecycle.register(
        tool=calculate,
        definition=updated_definition,
    )
)


print(
    "CHANGE:",
    change
)

print(
    "VERSION:",
    updated_record.version
)

print(
    "NEEDS REINDEX:",
    lifecycle.needs_reindex(
        "calculate"
    )
)


assert change.value == "updated"

assert updated_record.version == 2

assert lifecycle.needs_reindex(
    "calculate"
)


# ============================================================
# 5. Sync Updated Tool
# ============================================================

print("\n================ UPDATED SYNC ================")


result = synchronizer.sync(
    "calculate"
)


print(
    "SYNC RESULT:"
)

print(
    result
)


assert result["status"] == "indexed"

assert result["version"] == 2

assert (
    result["document_id"]
    == first_document_id
)


assert lifecycle.needs_reindex(
    "calculate"
) is False


# ============================================================
# 6. Third Sync - No Changes Again
# ============================================================

print("\n================ THIRD SYNC ================")


result = synchronizer.sync(
    "calculate"
)


print(
    "SYNC RESULT:"
)

print(
    result
)


assert result["status"] == "unchanged"

assert result["version"] == 2


# ============================================================
# Final
# ============================================================

print(
    "\n=================================================="
)

print(
    "TOOL INDEX SYNCHRONIZATION: ALL TESTS PASSED"
)

print(
    "=================================================="
)