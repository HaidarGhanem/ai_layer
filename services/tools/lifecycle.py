from enum import Enum

from services.tools.fingerprint import ToolFingerprint


class ToolChange(str, Enum):

    ADDED = "added"
    UPDATED = "updated"
    UNCHANGED = "unchanged"
    REMOVED = "removed"
    ENABLED = "enabled"
    DISABLED = "disabled"

from services.tools.record import ToolRecord


class ToolLifecycle:

    def __init__(
        self,
        registry,
    ):

        self.registry = registry

        self.fingerprint = ToolFingerprint()

    def register(
        self,
        tool,
        definition,
    ):

        fingerprint = (
            self.fingerprint.build(
                definition
            )
        )

        existing = (
            self.registry.get_record(
                definition.name
            )
        )

        if existing is None:

            record = self.registry.register(
                tool=tool,
                definition=definition,
            )

            record.fingerprint = fingerprint

            return (
                ToolChange.ADDED,
                record,
            )

        if existing.fingerprint == fingerprint:

            return (
                ToolChange.UNCHANGED,
                existing,
            )

        existing.tool = tool
        existing.definition = definition
        existing.fingerprint = fingerprint
        existing.version += 1
        existing.enabled = True

        return (
            ToolChange.UPDATED,
            existing,
        )

    def enable(
        self,
        name: str,
    ):

        changed = self.registry.enable(
            name
        )

        if not changed:

            return False

        return True

    def disable(
        self,
        name: str,
    ):

        changed = self.registry.disable(
            name
        )

        if not changed:

            return False

        return True

    def remove(
        self,
        name: str,
    ):

        return self.registry.remove(
            name
        )

    def needs_reindex(
        self,
        name: str,
    ) -> bool:

        record = (
            self.registry.get_record(
                name
            )
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

        record = (
            self.registry.get_record(
                name
            )
        )

        if record is None:

            raise ValueError(
                f"Tool '{name}' not found"
            )

        record.indexed_fingerprint = (
            record.fingerprint
        )