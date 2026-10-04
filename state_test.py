from services.loop.tools.calculator import calculate

from services.tools.register import ToolRegistry
from services.tools.lifecycle import ToolLifecycle
from services.tools.catalog_builder import ToolCatalogBuilder

from services.tools.postgres_state_store import (
    PostgresToolStateStore,
)


# ============================================================
# PostgreSQL Connection
# ============================================================

DB_DSN = (
    "postgresql://odoo_user:odoo_password@"
    "localhost:5432/odoo_db"
)


state_store = PostgresToolStateStore(
    dsn=DB_DSN,
    table_name="ai_tool_state_test",
)


# ============================================================
# Registry
# ============================================================

registry = ToolRegistry()


lifecycle = ToolLifecycle(
    registry=registry,
    state_store=state_store,
)


catalog_builder = ToolCatalogBuilder()


definition = catalog_builder.build(
    calculate,
    metadata={
        "source": "internal",
    },
)


# ============================================================
# 1. Clean Previous Test State
# ============================================================

print(
    "\n================ CLEAN STATE ================"
)

state_store.delete(
    definition.tool_id
)

print(
    "STATE CLEANED"
)


# ============================================================
# 2. Register
# ============================================================

print(
    "\n================ REGISTER ================"
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

assert record.version == 1

assert lifecycle.needs_reindex(
    "calculate"
)


# ============================================================
# 3. Mark Indexed
# ============================================================

print(
    "\n================ MARK INDEXED ================"
)

lifecycle.mark_indexed(
    "calculate"
)


state = state_store.get(
    definition.tool_id
)


print(
    "PERSISTED STATE:"
)

print(
    state
)


assert state is not None

assert (
    state.fingerprint
    == state.indexed_fingerprint
)

assert state.version == 1

assert lifecycle.needs_reindex(
    "calculate"
) is False


# ============================================================
# 4. Simulate Process Restart
# ============================================================

print(
    "\n================ PROCESS RESTART ================"
)

# New registry = new Python process equivalent
new_registry = ToolRegistry()

new_lifecycle = ToolLifecycle(
    registry=new_registry,
    state_store=state_store,
)


change, new_record = (
    new_lifecycle.register(
        tool=calculate,
        definition=definition,
    )
)


print(
    "CHANGE AFTER RESTART:",
    change
)

print(
    "VERSION:",
    new_record.version
)

print(
    "INDEXED FINGERPRINT:",
    new_record.indexed_fingerprint
)

print(
    "NEEDS REINDEX:",
    new_lifecycle.needs_reindex(
        "calculate"
    )
)


assert change.value == "unchanged"

assert new_record.version == 1

assert (
    new_record.indexed_fingerprint
    == new_record.fingerprint
)

assert new_lifecycle.needs_reindex(
    "calculate"
) is False


# ============================================================
# 5. Change Definition
# ============================================================

print(
    "\n================ CHANGE DEFINITION ================"
)

changed_definition = (
    catalog_builder.build(
        calculate,
        metadata={
            "source": "internal",
            "category": "arithmetic",
        },
    )
)


change, changed_record = (
    new_lifecycle.register(
        tool=calculate,
        definition=changed_definition,
    )
)


print(
    "CHANGE:",
    change
)

print(
    "VERSION:",
    changed_record.version
)

print(
    "NEEDS REINDEX:",
    new_lifecycle.needs_reindex(
        "calculate"
    )
)


assert change.value == "updated"

assert changed_record.version == 2

assert new_lifecycle.needs_reindex(
    "calculate"
)


# ============================================================
# 6. Persist Updated State
# ============================================================

print(
    "\n================ UPDATED STATE ================"
)

updated_state = state_store.get(
    changed_definition.tool_id
)


print(
    updated_state
)


assert updated_state.version == 2

assert (
    updated_state.fingerprint
    != updated_state.indexed_fingerprint
)


# ============================================================
# 7. Mark Updated Version Indexed
# ============================================================

print(
    "\n================ MARK UPDATED INDEXED ================"
)

new_lifecycle.mark_indexed(
    "calculate"
)


final_state = state_store.get(
    changed_definition.tool_id
)


print(
    final_state
)


assert final_state.version == 2

assert (
    final_state.fingerprint
    == final_state.indexed_fingerprint
)

assert new_lifecycle.needs_reindex(
    "calculate"
) is False


# ============================================================
# 8. Simulate Another Restart
# ============================================================

print(
    "\n================ SECOND RESTART ================"
)

another_registry = ToolRegistry()

another_lifecycle = ToolLifecycle(
    registry=another_registry,
    state_store=state_store,
)


change, restored_record = (
    another_lifecycle.register(
        tool=calculate,
        definition=changed_definition,
    )
)


print(
    "CHANGE:",
    change
)

print(
    "VERSION:",
    restored_record.version
)

print(
    "NEEDS REINDEX:",
    another_lifecycle.needs_reindex(
        "calculate"
    )
)


assert change.value == "unchanged"

assert restored_record.version == 2

assert another_lifecycle.needs_reindex(
    "calculate"
) is False


# ============================================================
# Final
# ============================================================

print(
    "\n=================================================="
)

print(
    "PERSISTENT TOOL STATE TESTS PASSED"
)

print(
    "=================================================="
)