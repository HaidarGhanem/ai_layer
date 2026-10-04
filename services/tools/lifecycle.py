from enum import Enum

from services.tools.fingerprint import ToolFingerprint
from services.tools.state import ToolIndexState


class ToolChange(str, Enum):

    ADDED = "added"
    UPDATED = "updated"
    UNCHANGED = "unchanged"
    REMOVED = "removed"
    ENABLED = "enabled"
    DISABLED = "disabled"


class ToolLifecycle:

    def __init__(
        self,
        registry,
        state_store,
    ):

        self.registry = registry
        self.state_store = state_store

        self.fingerprint = ToolFingerprint()

    def register(
        self,
        tool,
        definition,
    ):

        fingerprint = self.fingerprint.build(
            definition
        )

        tool_id = definition.tool_id

        if tool_id is None:

            raise ValueError(
                "Tool definition must have a tool_id"
            )

        persisted_state = (
            self.state_store.get(
                tool_id
            )
        )

        existing_record = (
            self.registry.get_record(
                tool.name
            )
        )

        # ----------------------------------------------------
        # New tool
        # ----------------------------------------------------

        if persisted_state is None:

            if existing_record is None:

                record = self.registry.register(
                    tool=tool,
                    definition=definition,
                )

            else:

                record = existing_record

            record.fingerprint = fingerprint

            record.version = 1

            record.indexed_fingerprint = None

            self.state_store.save(
                ToolIndexState(
                    tool_id=tool_id,
                    fingerprint=fingerprint,
                    indexed_fingerprint=None,
                    version=1,
                )
            )

            return (
                ToolChange.ADDED,
                record,
            )

        # ----------------------------------------------------
        # Existing tool - same definition
        # ----------------------------------------------------

        if persisted_state.fingerprint == fingerprint:

            if existing_record is None:

                record = self.registry.register(
                    tool=tool,
                    definition=definition,
                )

            else:

                record = existing_record

            record.fingerprint = fingerprint

            record.version = (
                persisted_state.version
            )

            record.indexed_fingerprint = (
                persisted_state.indexed_fingerprint
            )

            return (
                ToolChange.UNCHANGED,
                record,
            )

        # ----------------------------------------------------
        # Existing tool - changed definition
        # ----------------------------------------------------

        if existing_record is None:

            record = self.registry.register(
                tool=tool,
                definition=definition,
            )

        else:

            record = existing_record

            record.tool = tool
            record.definition = definition

        record.fingerprint = fingerprint

        record.version = (
            persisted_state.version + 1
        )

        record.indexed_fingerprint = (
            persisted_state.indexed_fingerprint
        )

        self.state_store.save(
            ToolIndexState(
                tool_id=tool_id,
                fingerprint=fingerprint,
                indexed_fingerprint=(
                    persisted_state.indexed_fingerprint
                ),
                version=record.version,
            )
        )

        return (
            ToolChange.UPDATED,
            record,
        )

    # ========================================================
    # Enable
    # ========================================================

    def enable(
        self,
        name: str,
    ):

        return self.registry.enable(
            name
        )

    # ========================================================
    # Disable
    # ========================================================

    def disable(
        self,
        name: str,
    ):

        return self.registry.disable(
            name
        )

    # ========================================================
    # Remove
    # ========================================================

    def remove(
        self,
        name: str,
    ):

        record = self.registry.get_record(
            name
        )

        if record is None:
            return None

        tool_id = record.definition.tool_id

        removed = self.registry.remove(
            name
        )

        if tool_id is not None:

            self.state_store.delete(
                tool_id
            )

        return removed

    # ========================================================
    # Re-index state
    # ========================================================

    def needs_reindex(
        self,
        name: str,
    ) -> bool:

        record = self.registry.get_record(
            name
        )

        if record is None:
            return False

        return (
            record.indexed_fingerprint
            != record.fingerprint
        )

    def mark_indexed(
        self,
        name: str,
    ):

        record = self.registry.get_record(
            name
        )

        if record is None:

            raise ValueError(
                f"Tool '{name}' not found"
            )

        record.indexed_fingerprint = (
            record.fingerprint
        )

        tool_id = record.definition.tool_id

        self.state_store.save(
            ToolIndexState(
                tool_id=tool_id,
                fingerprint=record.fingerprint,
                indexed_fingerprint=(
                    record.indexed_fingerprint
                ),
                version=record.version,
            )
        )