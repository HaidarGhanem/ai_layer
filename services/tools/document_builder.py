from services.tools.definition import ToolDefinition
from services.documents.document import DocumentService

class ToolDocumentBuilder:

    def __init__(self, document_service: DocumentService):
        self.document_service = document_service

    def build(self, definition: ToolDefinition):
        text = self._build_text(definition)
        metadata = {
            "type": "tool",
            "tool_name": definition.name,
            **definition.metadata
        }
        return self.document_service.create(
            text=text,
            metadata=metadata
        )

    def _build_text(self, definition: ToolDefinition) -> str:
        sections = [
            f"Tool: {definition.name}",
            f"Description: {definition.description}",
        ]

        input_text = self._build_input_text(
            definition.input_schema
        )

        if input_text:
            sections.append(f"Input: \n{input_text}")

        return "\n\n".join(sections)

    def _build_input_text(self, input_schema: dict) -> str :

        # name & details for all inputs
        properties = input_schema.get("properties", {})
        required = set(input_schema.get("required",[]))
        inputs = []
        for name, schema in properties.items():
            input_type = schema.get(
                "type",
                "unknowm"
            )

            requirement = (
                "required"
                if name in required 
                else "optional"
            )

            inputs.append(
                f"- {name}: {input_type} ({requirement})"
            )
        return "\n".join(inputs)