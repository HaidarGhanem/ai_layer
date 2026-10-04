import hashlib
import json

from services.tools.definition import ToolDefinition


class ToolFingerprint:

    def build(
        self,
        definition: ToolDefinition,
    ) -> str:

        payload = {
            "name": definition.name,
            "description": definition.description,
            "input_schema": definition.input_schema,
            "metadata": definition.metadata,
        }

        normalized = json.dumps(
            payload,
            sort_keys=True,
            ensure_ascii=False,
        )

        return hashlib.sha256(
            normalized.encode("utf-8")
        ).hexdigest()