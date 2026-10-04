from services.tools.definition import ToolDefinition
from services.tools.identity import ToolIdentity
from services.documents.document import DocumentService


class ToolDocumentBuilder:

    def __init__(
        self,
        document_service: DocumentService,
    ):
        self.document_service = document_service
        self.identity = ToolIdentity()

    def build(
        self,
        definition: ToolDefinition,
    ):

        tool_id = definition.tool_id

        if tool_id is None:

            tool_id = self.identity.build(
                name=definition.name,
                metadata=definition.metadata,
            )

        document_id = (
            self.identity.document_id(
                tool_id
            )
        )

        text = self._build_text(
            definition
        )

        metadata = {
            "type": "tool",
            "tool_name": definition.name,
            "tool_id": tool_id,
            **definition.metadata,
        }

        return self.document_service.create(
            text=text,
            metadata=metadata,
            document_id=document_id,
        )

    def _build_text(
        self,
        definition: ToolDefinition,
    ) -> str:

        sections = [
            f"Tool: {definition.name}",
            f"Description: {definition.description}",
        ]

        input_text = self._build_input_text(
            definition.input_schema
        )

        if input_text:

            sections.append(
                f"Inputs:\n{input_text}"
            )

        return "\n\n".join(
            sections
        )

    def _build_input_text(
        self,
        input_schema: dict,
    ) -> str:

        properties = input_schema.get(
            "properties",
            {}
        )

        required = set(
            input_schema.get(
                "required",
                []
            )
        )

        inputs = []

        for name, schema in properties.items():

            input_type = schema.get(
                "type",
                "unknown",
            )

            requirement = (
                "required"
                if name in required
                else "optional"
            )

            inputs.append(
                f"- {name}: "
                f"{input_type} "
                f"({requirement})"
            )

        return "\n".join(inputs)