from services.tools.definition import ToolDefinition
from services.tools.identity import ToolIdentity


class ToolCatalogBuilder:

    def __init__(self):

        self.identity = ToolIdentity()

    def build(
        self,
        tool,
        metadata: dict | None = None,
    ) -> ToolDefinition:

        metadata = {
            "type": "tool",
            **(metadata or {}),
        }

        tool_id = self.identity.build(
            name=tool.name,
            metadata=metadata,
        )

        input_schema = {}

        if hasattr(
            tool,
            "args_schema",
        ) and tool.args_schema:

            input_schema = (
                tool.args_schema
                .model_json_schema()
            )

        return ToolDefinition(
            name=tool.name,
            description=tool.description,
            input_schema=input_schema,
            metadata=metadata,
            tool_id=tool_id,
        )