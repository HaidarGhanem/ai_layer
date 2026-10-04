from services.loop.tools.calculator import calculate

from services.tools.register import ToolRegistry
from services.tools.lifecycle import ToolLifecycle
from services.tools.catalog_builder import ToolCatalogBuilder


registry = ToolRegistry()

lifecycle = ToolLifecycle(
    registry=registry
)

catalog_builder = ToolCatalogBuilder()


definition = catalog_builder.build(
    calculate,
    metadata={
        "source": "internal",
    },
)


# ============================================================
# 1. First registration
# ============================================================

change, record = lifecycle.register(
    tool=calculate,
    definition=definition,
)

print("\nFIRST REGISTER:")
print("CHANGE:", change)
print("VERSION:", record.version)
print("FINGERPRINT:", record.fingerprint)
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
# 2. Mark indexed
# ============================================================

lifecycle.mark_indexed(
    "calculate"
)

print("\nAFTER INDEX:")
print(
    "NEEDS REINDEX:",
    lifecycle.needs_reindex(
        "calculate"
    )
)

assert lifecycle.needs_reindex(
    "calculate"
) is False


# ============================================================
# 3. Register exactly same definition
# ============================================================

change, same_record = (
    lifecycle.register(
        tool=calculate,
        definition=definition,
    )
)

print("\nSAME DEFINITION:")
print("CHANGE:", change)
print("VERSION:", same_record.version)

assert change.value == "unchanged"
assert same_record.version == 1

assert lifecycle.needs_reindex(
    "calculate"
) is False


# ============================================================
# 4. Change the definition
# ============================================================

changed_definition = (
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
        definition=changed_definition,
    )
)

print("\nCHANGED DEFINITION:")
print("CHANGE:", change)
print("VERSION:", updated_record.version)
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
# 5. Mark updated version indexed
# ============================================================

lifecycle.mark_indexed(
    "calculate"
)

print("\nAFTER UPDATED INDEX:")
print(
    "NEEDS REINDEX:",
    lifecycle.needs_reindex(
        "calculate"
    )
)

assert lifecycle.needs_reindex(
    "calculate"
) is False


# ============================================================
# 6. Disable
# ============================================================

result = lifecycle.disable(
    "calculate"
)

print("\nDISABLE:")
print("RESULT:", result)
print(
    "REGISTRY GET:",
    registry.get("calculate")
)

assert result is True

assert (
    registry.get("calculate")
    is None
)


# ============================================================
# 7. Enable
# ============================================================

result = lifecycle.enable(
    "calculate"
)

print("\nENABLE:")
print("RESULT:", result)
print(
    "REGISTRY GET:",
    registry.get("calculate")
)

assert result is True

assert (
    registry.get("calculate")
    is calculate
)


# ============================================================
# 8. Remove
# ============================================================

removed = lifecycle.remove(
    "calculate"
)

print("\nREMOVE:")
print("REMOVED:", removed)

assert removed is not None

assert (
    registry.get_record(
        "calculate"
    )
    is None
)


print(
    "\nALL TOOL LIFECYCLE V2 TESTS PASSED"
)