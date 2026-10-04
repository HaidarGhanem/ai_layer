from services.tools.lifecycle import ToolLifecycle


class ToolIndexSynchronizer:

    def __init__(
        self,
        vector_store,
        document_builder,
        ingestion,
        lifecycle: ToolLifecycle,
    ):

        self.vector_store = vector_store
        self.document_builder = document_builder
        self.ingestion = ingestion
        self.lifecycle = lifecycle

    def sync(
        self,
        tool_name: str,
    ):

        record = self.lifecycle.registry.get_record(
            tool_name
        )

        if record is None:

            raise ValueError(
                f"Tool '{tool_name}' not found"
            )

        if not self.lifecycle.needs_reindex(
            tool_name
        ):

            return {
                "status": "unchanged",
                "tool_name": tool_name,
                "version": record.version,
            }

        document = self.document_builder.build(
            record.definition
        )

        nodes = self.ingestion.run(
            documents=[document]
        )

        if record.indexed_fingerprint is not None:

            self.vector_store.delete(
                document.id_
            )

        self.vector_store.add(
            nodes
        )

        self.lifecycle.mark_indexed(
            tool_name
        )

        return {
            "status": "indexed",
            "tool_name": tool_name,
            "version": record.version,
            "document_id": document.id_,
            "nodes": len(nodes),
        }

    def remove(
        self,
        document_id: str,
    ):

        self.vector_store.delete(
            document_id
        )

        return {
            "status": "removed",
            "document_id": document_id,
        }